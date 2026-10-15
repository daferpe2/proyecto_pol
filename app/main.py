from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI,status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import SQLModel

from app.operations.checkroles import require_role
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


@asynccontextmanager
async def lifespan(app:FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(lifespan=lifespan)

app.mount("/app/static/",StaticFiles(directory="app/static/"),name="static")


@app.get("/crypto/key")
def get_crypto_key(user=Depends(get_current_user_id)):
    if not isinstance(user,UserTable):
        return RedirectResponse("/",status_code=status.HTTP_401_UNAUTHORIZED)

    require_role([Rol.analista,Rol.coordinador,Rol.jefe,Rol.qc,Rol.qc_s,Rol.registro])
    return {"key": {"AES_KEY_BASE64":settings.settings.AES_KEY_BASE64}}


# @app.middleware("http")
# async def auth_middleware(request: Request, call_next):
#     if request.url.path in ["/", "/inicio_secion"]:
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