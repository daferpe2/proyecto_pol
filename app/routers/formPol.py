import asyncio
import base64
import json
import os
from datetime import datetime

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.operations.autentiacion_funciones import get_current_user_id
from app.operations.buscador_rdp_csv import procesar_excel_job
from app.operations.checkroles import check_roles, require_role
from app.operations.crudAuditoria import create_registro_auditoria
from app.operations.crudPoligraf import (
    create_registro,
    delete_registro,
    get_registro,
    get_registros,
    get_registros_busqueda,
    get_registros_busqueda_regional,
    get_registros_regional,
)
from app.operations.encryptedpayload import AES_KEY, EncryptedPayload
from app.operations.keyset import keyset_query
from db import SessionDep
from models import (
    EstadosValidacion,
    JobEstado,
    PdpPoligrafistasTabla,
    PdpPoligrafistasTablaPublic,
    PdpPoligrafistasTablaPublicCreate,
    PdpPoligrafistasUpdate,
    RDPAuditoria,
    RDPJob,
    Rol,
    UserTable,
)

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(prefix="/tabla-poligraf", tags=["TablaBasePol"])


# @router.get("/rdp", response_class=HTMLResponse)
# async def pagina_rdp(
#     request: Request,
#     session: SessionDep,
#     q: str | None = None,
#     limit: int = 5,
#     offset: int = 0,
#     user: UserTable = Depends(require_role([
#         Rol.qc,
#         Rol.qc_s,
#         Rol.analista,
#         Rol.jefe,
#         Rol.super_admin
#     ]))
# ):
#     # 1. Obtener registros según búsqueda o lista normal
#     if q:
#         registros = await get_registros_busqueda(q, session, limit, offset)
#     else:
#         registros = await get_registros(session, limit, offset)

#     # 2. Filtrar por región según el rol
#     registros_filtrados = []

#     for rdp in registros:

#         # SUPER_ADMIN ve todo
#         if user.rol == Rol.super_admin:
#             registros_filtrados.append(rdp)
#             continue

#         # QC / QC_S → región o comisión
#         if user.rol in [Rol.qc, Rol.qc_s]:
#             if rdp.regional in [user.regional, user.regional_comision]:
#                 registros_filtrados.append(rdp)
#             continue

#         # ANALISTA / JEFE → solo su región
#         if user.rol in [Rol.analista, Rol.jefe]:
#             if rdp.regional == user.regional:
#                 registros_filtrados.append(rdp)
#             continue

#     # 3. Renderizar plantilla
#     return templates.TemplateResponse(
#         "lista_rdp.html",
#         {   
#             "user": user,
#             "request": request,
#             "registros": registros_filtrados,
#             "limit": limit,
#             "offset": offset,
#             "q": q,
#             "user": user
#         }
#     )


@router.get("/rdp", response_class=HTMLResponse)
async def pagina_rdp(
    request: Request,
    session: SessionDep,
    q: str | None = None,
    limit: int = 5,
    offset: int = 0,
    user: UserTable = Depends(get_current_user_id)
):
    # 1. Obtener registros según búsqueda o lista normal
    check_roles(user)
    if q:
        registros = await get_registros_busqueda(q, session, limit, offset)
    else:
        registros = await get_registros(session, limit, offset)

    return templates.TemplateResponse(
        "lista_rdp.html",
        {   
            "user": user,
            "request": request,
            "limit": limit,
            "offset": offset,
            "q": q,
            "registros":registros
        }
    )



@router.get("/resultados-rdp/form")
async def form_resultados_rdp(
    request: Request,
    session: SessionDep,
    user: UserTable = Depends(get_current_user_id)
):

    if user is None:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse(
        "form_resultados_rdp.html",
        {
            "request": request,
            "title": "Resultados Obtenidos RDP",
            "user": user
        }
    )


@router.post("/create_poli", response_model=PdpPoligrafistasTablaPublic)
async def crear(data: EncryptedPayload, 
                session: SessionDep,
                user: UserTable = Depends(get_current_user_id)):
    if not isinstance(user,UserTable):
        return RedirectResponse("/",status_code=status.HTTP_303_SEE_OTHER)
    aesgcm = AESGCM(AES_KEY)

    iv = base64.b64decode(data.iv)
    payload = base64.b64decode(data.payload)

    decrypted_bytes = aesgcm.decrypt(iv, payload, None)
    decrypted_json = decrypted_bytes.decode("utf-8")

    fields = json.loads(decrypted_json)

    
    fields["texto_busqueda"] = f"{fields["no_cedula"]} {fields['apellidos_nombres']}"

    objs = PdpPoligrafistasTablaPublicCreate(**fields)


    create_db = await create_registro(data=objs, session=session)
    return create_db



@router.get("/consulta_poli/{registro_id}", response_model=PdpPoligrafistasTablaPublic)
async def obtener(registro_id: int, session: SessionDep,
                  user: UserTable = Depends(get_current_user_id)):

    if not isinstance(user,UserTable):
        return RedirectResponse("/",status_code=status.HTTP_303_SEE_OTHER)

    registro = await get_registro(session, registro_id)
    if not registro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro no encontrado")
    return JSONResponse(content=jsonable_encoder(registro))


@router.get("/lista_rdp", response_model=list[PdpPoligrafistasTablaPublic])
async def listar_rdp(
    request: Request,
    session: SessionDep,
    q: str | None = None,
    limit: int = 5,
    offset: int = 0,
    user: UserTable = Depends(get_current_user_id)
):
    # 1. Obtener registros según búsqueda o lista normal
    check_roles(user)
    
    if q:
        registros = await get_registros_busqueda(q, session, limit, offset)
    else:
        registros = await get_registros(session, limit, offset)

    # 2. Filtrar por región según el rol

    # 3. Renderizar plantilla
    return templates.TemplateResponse(
        "lista_rdp.html",
        {
            "user": user,
            "request": request,
            "registros": registros,
            "limit": limit,
            "offset": offset,
            "q": q or ""
        }
    )





@router.post("/actualizacion_poli/{registro_id}")
async def actualizar(session: SessionDep, 
                     registro_id: int, 
                     data: EncryptedPayload,
                     user: UserTable = Depends(get_current_user_id)):
    
    if not isinstance(user,UserTable):
        return RedirectResponse("/",status_code=status.HTTP_302_FOUND)
    aesgcm = AESGCM(AES_KEY)

    iv = base64.b64decode(data.iv)
    payload = base64.b64decode(data.payload)

    try:
        decrypted_bytes = aesgcm.decrypt(iv, payload, None)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error al descifrar datos")

    decrypted_json = decrypted_bytes.decode("utf-8")
    fields = json.loads(decrypted_json)

    # 2. Convertir a modelo de update
    update_data = PdpPoligrafistasUpdate(**fields)



    # 3. Obtener registro actual
    registro = await get_registro(session,registro_id)


    if not registro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro no encontrado")

    # 4. Actualizar solo campos con valor (mantener anteriores si vienen vacíos)
    for field_name, value in update_data.model_dump().items():
        if value is None:
            continue

        if isinstance(value, str) and value.strip() == "":
            continue

        setattr(registro, field_name, value)
    # 4.1 Recalcular texto_busqueda con los valores finales del registro
    registro.texto_busqueda = f"{registro.no_cedula or ''} {registro.apellidos_nombres or ''}".strip()

    # 5. Actualizar fecha_registro como fecha de modificación (tu opción B)
    registro.fecha_act = datetime.now()
    registro.ain = update_data.ain


    # 6. Guardar cambios
    session.add(registro)
    session.commit()
    session.refresh(registro)
    
    creacion_registro = RDPAuditoria(rdp_id=registro.id,
                                           auditor_id=user.id,comentarios=fields["comentarios"],
                                           fecha=registro.fecha_act)

    await create_registro_auditoria(data=creacion_registro,session=session)

    return {"message": "Registro actualizado correctamente"}



@router.post("/borrar_poli/{registro_id}")
async def eliminar(registro_id: int, session: SessionDep,
                   user: UserTable = Depends(get_current_user_id)):
    check_roles(user=user)
    registro = await delete_registro(session, registro_id)
    if not registro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro no encontrado")
    return RedirectResponse("/tabla-poligraf/rdp",status_code=status.HTTP_303_SEE_OTHER)


@router.post("/borrar_poli_regional/{registro_id}")
async def eliminar_regional(registro_id: int, session: SessionDep):
    require_role([Rol.qc])
    registro = await delete_registro(session, registro_id)
    if not registro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro no encontrado")
    return RedirectResponse("/tabla-poligraf/lista_rdp_regional_f",status_code=status.HTTP_303_SEE_OTHER)



@router.get("/editar_rdp/{registro_id}", response_class=HTMLResponse)
async def editar_rdp(
    registro_id: int,
    request: Request,
    session: SessionDep,
    user: UserTable = Depends(get_current_user_id)
):
   

    if not isinstance(user, UserTable):
        return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)

    # check_roles(user=user) 

    registro = await get_registro(session=session,registro_id=registro_id)


    if not registro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro no encontrado")


    return templates.TemplateResponse(
        "form_editar_rdp.html",
        {
            "request": request,
            "registro": registro,
            "user": user

        }
    )


@router.get("/editar_rdp_regional/{registro_id}", response_class=HTMLResponse)
async def editar_rdp_regional(
    registro_id: int,
    request: Request,
    session: SessionDep,
    user: UserTable = Depends(get_current_user_id)
):

    require_role([Rol.qc])


    if not isinstance(user, UserTable):
        return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)

    registro = await get_registro(session=session,registro_id=registro_id)

    if user.regional != registro.regional:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No tiene acceso a esta área")

    if not registro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro no encontrado")


    return templates.TemplateResponse(
        "form_editar_rdp.html",
        {
            "request": request,
            "registro": registro,
            "user": user

        }
    )



# Consultas Regionales


@router.get("/lista_rdp_fragment")
async def lista_rdp_fragment(
    request: Request,
    session: SessionDep,
    last_id: int | None = None,
    limit: int = 5,
    direction: str = "next",
    user: UserTable = Depends(get_current_user_id)
):
    require_role([Rol.qc])
    filters = [PdpPoligrafistasTabla.regional == user.regional,
               PdpPoligrafistasTabla.estado == EstadosValidacion.PENDIENTE]

    items, next_cursor = keyset_query(
        session=session,
        model=PdpPoligrafistasTabla,
        last_id=last_id,
        limit=limit,
        filters=filters
    )

    return templates.TemplateResponse(
        "fragment_rdp_cards.html",
        {
            "request": request,
            "registros": items,
            "next_cursor": next_cursor,
            "user": user
        }
    )





@router.post("/upload")
async def upload_csv_rdp(
    session: SessionDep,
    file: UploadFile = File(...),
    user: UserTable = Depends(get_current_user_id),
):
    if not isinstance(user, UserTable):
        return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)

    check_roles(user)

    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Archivo demasiado grande (máx 5 MB)"
        )

    # Crear job en la tabla correcta
    job = RDPJob(usuario=user.nombre_apellido)
    session.add(job)
    session.commit()
    session.refresh(job)

    asyncio.create_task(procesar_excel_job(job.id, content))

    return {"job_id": job.id, "estado": job.estado}




@router.get("/result/{job_id}")
def estado_o_descarga_job(
    job_id: int,
    db: SessionDep,
    user = Depends(get_current_user_id),
    descargar: bool = False,
):
    job = db.get(RDPJob, job_id)

    # 🔥 ESTA LÍNEA ES LA CLAVE
    db.refresh(job)

    if not job:
        return {"estado": "ERROR", "error_detalle": "Job no encontrado"}

    if job.usuario != user.nombre_apellido:
        return {"estado": "ERROR", "error_detalle": "No tienes permiso para este job"}

    if job.estado in {JobEstado.PENDIENTE, JobEstado.EN_PROCESO}:
        return {"estado": job.estado}

    if job.estado in {JobEstado.ERROR, JobEstado.INTERRUMPIDO}:
        return {"estado": job.estado, "error_detalle": job.error_detalle}

    if not descargar:
        return {"estado": "COMPLETADO"}

    ruta = job.ruta_archivo_resultado
    if not ruta or not os.path.exists(ruta):
        return {"estado": "EXPIRADO"}

    return FileResponse(
        ruta,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=f"resultado_job_rdp_{job_id}.xlsx"
    )




@router.get("/lista_rdp_regional_f", response_model=list[PdpPoligrafistasTablaPublic])
async def listar_rdp_regional(
    request: Request,
    session: SessionDep,
    q: str | None = None,
    limit: int = 5,
    offset: int = 0,
    user: UserTable = Depends(get_current_user_id)
):
    # 1. Obtener registros según búsqueda o lista normal
    require_role([Rol.qc])
    
    if q:
        registros = await get_registros_busqueda_regional(q, user.regional ,session, limit, offset)
    else:
        registros = await get_registros_regional(user.regional,session, limit, offset)

    # 2. Filtrar por región según el rol

    # 3. Renderizar plantilla
    return templates.TemplateResponse(
        "resultados_poligraficos_regionales.html",
        {
            "user": user,
            "request": request,
            "registros": registros,
            "limit": limit,
            "offset": offset,
            "q": q or ""
        }
    )
