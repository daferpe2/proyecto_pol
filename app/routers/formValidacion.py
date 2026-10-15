from datetime import datetime,UTC

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.operations.autentiacion_funciones import get_current_user_id
from app.operations.checkroles import check_roles, require_role
from app.operations.crudAuditoria import get_registro_rdp, get_registros_rdp
from app.operations.crudPoligraf import get_count_rdp_validacion, get_count_rdp_validacion_regional, get_count_rdp_validacion_semana, get_count_rdp_validacion_semana_reginal, get_registro
from db import SessionDep
from models import UserTable,Rol

router = APIRouter(prefix="/validacion", tags=["Validacion"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/auditor/rdp", response_class=HTMLResponse)
async def mostrar_rdp_auditor(
    request: Request,
    db: SessionDep,
    usuario: UserTable = Depends(get_current_user_id)
):
    check_roles(user=usuario)

    conteo_validacion = await get_count_rdp_validacion(session=db)

    consulta_semana = await get_count_rdp_validacion_semana(session=db)



    # 3. Renderizar plantilla
    return templates.TemplateResponse(
        "form_validacion.html",
        {
            "request": request,
            "fecha_consulta": datetime.now(),
            "user":usuario,
            "pendientes": conteo_validacion[0],
            "aprobados": conteo_validacion[1],
            "rechazados": conteo_validacion[2],
            "conteo_semanal":consulta_semana
        }
    )


@router.get("/auditor/rdp-regional", response_class=HTMLResponse)
async def mostrar_rdp_auditor_regional(
    request: Request,
    db: SessionDep,
    usuario: UserTable = Depends(get_current_user_id)
):
    require_role(roles_permitidos=[Rol.qc])

    regional = usuario.regional
    conteo_validacion = await get_count_rdp_validacion_regional(session=db,regional=regional)

    consulta_semana = await get_count_rdp_validacion_semana_reginal(session=db,regional=usuario.regional)

    # 3. Renderizar plantilla
    return templates.TemplateResponse(
        "form_validacion_regional.html",
        {
            "request": request,
            "fecha_consulta": datetime.now(),
            "user":usuario,
            "pendientes": conteo_validacion[0],
            "aprobados": conteo_validacion[1],
            "rechazados": conteo_validacion[2],
            "conteo_semanal":consulta_semana
        }
    )
