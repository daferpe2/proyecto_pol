import asyncio
import os

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse,RedirectResponse

from app.operations.autentiacion_funciones import get_current_user_id
from app.operations.checkroles import check_roles
from app.operations.generacion_documento import numero_documento
from app.operations.procesador_asincrono import procesar_csv_job
from db import SessionDep
from models import BuscadorJob, JobEstado, UserTable

router = APIRouter(prefix="/buscador-csv",tags=["Buscarod_csv"])

@router.post("/upload")
async def upload_csv(
    session: SessionDep,
    file: UploadFile = File(...),
    user: UserTable = Depends(get_current_user_id),

):
    if not isinstance(user, UserTable):
        return RedirectResponse("/",status_code=status.HTTP_303_SEE_OTHER)
    
    check_roles(user)

    # Validar tamaño máximo (5 MB)
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archivo demasiado grande (máx 5 MB)")

    csv_text = content.decode("utf-8", errors="ignore")

    # Crear job
    job = BuscadorJob(usuario=user.nombre_apellido)
    session.add(job)
    session.commit()
    session.refresh(job)

    # Lanzar procesamiento asincrónico
    asyncio.create_task(procesar_csv_job(job.id, csv_text))

    return {"job_id": job.id, "estado": job.estado}



@router.get("/result/{job_id}")
def estado_o_descarga_job(
    job_id: int,
    db: SessionDep,
    user = Depends(get_current_user_id),
    descargar: bool = False,
):
    job = db.get(BuscadorJob, job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job no encontrado")

    if job.usuario != user.nombre_apellido:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No tienes permiso para este job")

    # Estados del job
    if job.estado in {JobEstado.PENDIENTE, JobEstado.EN_PROCESO}:
        return {"estado": job.estado}

    if job.estado in {JobEstado.ERROR, JobEstado.INTERRUMPIDO}:
        return {"estado": job.estado, "error_detalle": job.error_detalle}

    # COMPLETADO → devolver JSON si descargar=false
    if not descargar:
        return {"estado": "COMPLETADO"}

    # COMPLETADO → descargar archivo si descargar=true
    ruta = job.ruta_archivo_resultado
    if not ruta or not os.path.exists(ruta):
        return {"estado": "EXPIRADO"}

    return FileResponse(
        ruta,
        media_type="text/csv",
        filename=f"resultado_job_{numero_documento()}.csv"
    )
