import asyncio
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI,status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import SQLModel

from app.operations.checkroles import require_role
from app.taks.cleanup import tarea_borrado_semanal
from app.taks.scheduler import tarea_limpieza
import settings
from app.operations.autentiacion_funciones import get_current_user_id
from app.routers import (
    autenticacion,
    buscador_csv,
    busqueda_esp,
    cargamasiva,
    formEsp,
    formPol,
    formValidacion,
    inicio,
    unidades,
    log_usuarios
)
from db import engine
from models import Rol, UserTable
from apscheduler.schedulers.asyncio import AsyncIOScheduler


@asynccontextmanager
async def lifespan(app:FastAPI):
    SQLModel.metadata.create_all(engine)
    asyncio.create_task(tarea_borrado_semanal())
    # scheduler = AsyncIOScheduler()

    # Ejecutar cada semana
    # scheduler.add_job(
    #     tarea_limpieza,
    #     trigger="cron",
    #     day_of_week="mon",   # lunes
    #     hour=3,              # 03:00 AM
    #     minute=0
    # )

    # scheduler.add_job(
    #     tarea_limpieza,
    #     trigger="interval",
    #     minutes=1
    # )

    # Si quieres mensual:
    # scheduler.add_job(tarea_limpieza, trigger="cron", day=1, hour=3, minute=0)

    # scheduler.start()
    # print("✔ APScheduler iniciado")

    # yield

    # scheduler.shutdown()
    # print("✔ APScheduler detenido")
    yield

app = FastAPI(lifespan=lifespan)

app.mount("/app/static/",StaticFiles(directory="app/static/"),name="static")


@app.get("/crypto/key")
def get_crypto_key(user=Depends(get_current_user_id)):
    if not isinstance(user,UserTable):
        return RedirectResponse("/",status_code=status.HTTP_401_UNAUTHORIZED)

    require_role([Rol.analista,Rol.coordinador,Rol.jefe,Rol.qc,Rol.qc_s,Rol.registro])
    return {"key": {"AES_KEY_BASE64":settings.settings.AES_KEY_BASE64}}


@app.get("/crypto/login-public-key")
async def get_login_public_key():
    """
    Devuelve la llave pública RSA para el login.
    Este endpoint NO debe requerir autenticación.
    """
    with open("keys\LOGIN_PUBLIC_KEY.pem", "r") as f:
        public_key_pem = f.read()

    return {"public_key": public_key_pem}


# @app.middleware("http")
# async def auth_middleware(request: Request, call_next):
#     if request.url.path in ["/", "/inicio_sesion"]:
#         return await call_next(request)

#     token = request.cookies.get("access_token")
#     if not token:
#         return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

#     return await call_next(request)

app.include_router(inicio.router)
app.include_router(formEsp.router)
app.include_router(formPol.router)
app.include_router(autenticacion.router)
app.include_router(unidades.router)
app.include_router(busqueda_esp.router)
app.include_router(buscador_csv.router)
app.include_router(formValidacion.router)
app.include_router(cargamasiva.router)
app.include_router(log_usuarios.router)