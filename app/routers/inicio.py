from datetime import datetime

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.operations.autentiacion_funciones import get_current_user_id
from models import UserTable

router = APIRouter()

router.mount("/app/static/css",StaticFiles(directory="app/static/css"))

templates = Jinja2Templates(directory="app/templates")

@router.get("/home", response_class=HTMLResponse)
async def home(
    request: Request,
    user: UserTable = Depends(get_current_user_id)
):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "user":user,
            "date": datetime.now()
            }
    )

# @router.get("/home", response_class=HTMLResponse)
# async def home(
#     request: Request,
#     db: SessionDep,
#     usuario: UserTable = Depends(get_current_user_id)
# ):
#     check_roles(user=usuario)

#     conteo_validacion = await get_count_rdp_validacion(session=db)

#     consulta_semana = await get_count_rdp_validacion_semana(session=db)

#     # 3. Renderizar plantilla
#     return templates.TemplateResponse(
#         "form_validacion.html",
#         {
#             "request": request,
#             "fecha_consulta": datetime.now(),
#             "user":usuario,
#             "pendientes": conteo_validacion[0],
#             "aprobados": conteo_validacion[1],
#             "conteo_semanal":consulta_semana
#         }
#     )