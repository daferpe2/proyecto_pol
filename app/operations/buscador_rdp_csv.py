import asyncio
import csv
import io
import os
import uuid
from datetime import datetime

from sqlmodel import Session, select

from db import engine  # donde tengas tu engine de SQLModel
from models import (  # ajusta import según tu proyecto
    JobEstado,
    PdpPoligrafistasTabla,
    RDPJob,
)

SEM_MAX = 10
RESULTS_DIR = "results"


async def procesar_csv_job(job_id: int, csv_text: str):
    """
    Procesa un CSV asociado a un job:
    - Lee filas del CSV.
    - Busca en TablaBaseEspF usando text_buscador.
    - Genera un CSV de resultados.
    - Actualiza el job con ruta del archivo y estado final.
    """
    loop = asyncio.get_event_loop()
    sem = asyncio.Semaphore(SEM_MAX)

    # -----------------------------
    # Helpers síncronos de BD
    # -----------------------------
    def sync_get_job():
        with Session(engine) as session:
            return session.get(RDPJob, job_id)

    def sync_set_estado(estado: JobEstado, error: str | None = None):
        with Session(engine) as session:
            job = session.get(RDPJob, job_id)
            if not job:
                return
            job.estado = estado
            job.error_detalle = error
            job.fecha_actualizacion = datetime.now()
            session.add(job)
            session.commit()

    def sync_set_ruta(ruta: str):
        with Session(engine) as session:
            job = session.get(RDPJob, job_id)
            if not job:
                return
            job.ruta_archivo_resultado = ruta
            job.fecha_actualizacion = datetime.now()
            session.add(job)
            session.commit()

    # -----------------------------
    # 1. Obtener job y marcar EN_PROCESO
    # -----------------------------
    job = await loop.run_in_executor(None, sync_get_job)
    if not job:
        return

    await loop.run_in_executor(None, lambda: sync_set_estado(JobEstado.EN_PROCESO))

    try:
        # -----------------------------
        # 2. Parsear CSV de entrada
        # -----------------------------
        reader = csv.DictReader(io.StringIO(csv_text), delimiter=";")
        filas = list(reader)

        resultados: list[dict] = []

        # -----------------------------
        # 3. Función síncrona de búsqueda
        # -----------------------------
        def sync_buscar_por_criterio(criterio: str):
            with Session(engine) as session:
                stmt = select(PdpPoligrafistasTabla).where(
                    PdpPoligrafistasTabla.texto_busqueda.ilike(f"%{criterio}%")
                )
                return session.exec(stmt).all()

        # -----------------------------
        # 4. Procesar cada fila con semáforo
        # -----------------------------
        async def procesar_fila(fila: dict):
            async with sem:
                no_cedula = (fila.get("no_cedula") or "").strip()
                apellidos_nombres = (fila.get("apellidos_nombres") or "").strip()
                criterio = f"{no_cedula} {apellidos_nombres}".strip()

                try:
                    rows = await loop.run_in_executor(
                        None, lambda: sync_buscar_por_criterio(criterio)
                    )

                    if not rows:
                        resultados.append({
                            "input_no_cedula": no_cedula,
                            "input_apellidos_nombre": apellidos_nombres,
                            "criterio_busqueda": criterio,
                            "estado": "SIN_RESULTADOS",
                            "detalle_error": "",
                            "resultados": [],
                        })
                        return

                    registros = []
                    inconsistencia = False

                    for r in rows:
                        if r.no_cedula != no_cedula or r.apellidos_nombres != apellidos_nombres:
                            inconsistencia = True

                        registros.append({
                            "no_cedula": r.no_cedula,
                            "apellidos_nombre": r.apellidos_nombres,
                            "categoria": r.categoria,
                        })

                    estado = "INCONSISTENCIA_DATOS" if inconsistencia else "OK"
                    detalle = (
                        "La cédula y el nombre no coinciden con los registros encontrados"
                        if inconsistencia else ""
                    )

                    resultados.append({
                        "input_no_cedula": no_cedula,
                        "input_apellidos_nombre": apellidos_nombres,
                        "criterio_busqueda": criterio,
                        "estado": estado,
                        "detalle_error": detalle,
                        "resultados": registros,
                    })

                except Exception as e:
                    resultados.append({
                        "input_no_cedula": no_cedula,
                        "input_apellidos_nombre": apellidos_nombres,
                        "criterio_busqueda": criterio,
                        "estado": "ERROR_BD",
                        "detalle_error": str(e),
                        "resultados": [],
                    })

        # Lanzar todas las tareas
        await asyncio.gather(*(procesar_fila(f) for f in filas))

        # -----------------------------
        # 5. Generar CSV final en memoria
        # -----------------------------
        output = io.StringIO()
        writer = csv.writer(output, delimiter=";")

        writer.writerow([
            "input_no_cedula",
            "input_apellidos_nombre",
            "criterio_busqueda",
            "estado",
            "detalle_error",
            "resultado_no_cedula",
            "resultado_apellidos_nombre",
            "resultado_observacion",
        ])

        for r in resultados:
            if not r["resultados"]:
                writer.writerow([
                    r["input_no_cedula"],
                    r["input_apellidos_nombre"],
                    r["criterio_busqueda"],
                    r["estado"],
                    r["detalle_error"],
                    "",
                    "",
                    "",
                ])
            else:
                for reg in r["resultados"]:
                    writer.writerow([
                        r["input_no_cedula"],
                        r["input_apellidos_nombre"],
                        r["criterio_busqueda"],
                        r["estado"],
                        r["detalle_error"],
                        reg["no_cedula"],
                        reg["apellidos_nombre"],
                        reg["observacion"],
                    ])

        # -----------------------------
        # 6. Escribir CSV a disco
        # -----------------------------
        if not os.path.exists(RESULTS_DIR):
            os.makedirs(RESULTS_DIR, exist_ok=True)

        filename = f"resultado_job_csv{job_id}_{uuid.uuid4().hex}.csv"
        ruta = os.path.join(RESULTS_DIR, filename)

        with open(ruta, "w", encoding="utf-8", newline="") as f:
            f.write(output.getvalue())

        # -----------------------------
        # 7. Actualizar job con ruta y estado COMPLETADO
        # -----------------------------
        await loop.run_in_executor(None, lambda: sync_set_ruta(ruta))
        await loop.run_in_executor(None, lambda: sync_set_estado(JobEstado.COMPLETADO))

    except Exception:
        # -----------------------------
        # 8. Manejo de error global del job
        # -----------------------------
        await loop.run_in_executor(None, lambda: sync_set_estado(JobEstado.ERROR, str(e)))

