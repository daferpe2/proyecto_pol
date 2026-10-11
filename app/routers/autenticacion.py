from typing import Annotated

from fastapi import APIRouter, Form, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.params import Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.operations.autentiacion_funciones import (
    SECRET_KEY,
    TIME_EXPIRE,
    get_current_user,
)
from app.operations.crud_usuarios import (
    create_registro,
    delete_registro,
    get_registro,
    get_registros,
    update_registro,
)
from app.operations.token_manager import TokenManager
from db import SessionDep
from models import UserTable, UsuarioCreate, UsuarioPublic, UsuarioRead, UsuarioUpdate
from password import get_password_hass


def get_token_manager():
    return TokenManager(secret_key=SECRET_KEY)

router = APIRouter(tags=["Usuario"])


router.mount("/app/static/css",StaticFiles(directory="app/static/css"))


templates = Jinja2Templates(directory="app/templates")


@router.get("/",response_class=HTMLResponse)
async def auth_fomr(request:Request):
    return templates.TemplateResponse("formulario_ingreso.html",{"request":request})


@router.post("/inicio_secion")
async def login_user(
    session: SessionDep,
    email: Annotated[str, Form(...)],
    password: Annotated[str, Form(...)],
    token_manager: TokenManager = Depends(get_token_manager)
):
    email = email.strip()

    # Validación correcta
    db_p = get_current_user(session=session, email=email, password=password)

    if not isinstance(db_p, UserTable):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No autorizado"
        )

    # Crear token seguro
    token = token_manager.create_token({
        'id': db_p.id,
        'role': db_p.rol
    })

    response = RedirectResponse("/home", status_code=status.HTTP_302_FOUND)

    # Cookie del usuario
    response.set_cookie(
        key="user_id",
        value=str(db_p.id),
        max_age=TIME_EXPIRE,
        httponly=True,      # Debe ser True
        secure=False,       # Cambiar a True en producción
        samesite="Lax",
        path="/"            # Debe ser "/" para que exista en toda la app
    )

    # Cookie del token
    response.set_cookie(
        key="access_token",
        value=token,
        max_age=TIME_EXPIRE,
        httponly=True,      # Debe ser True
        secure=False,       # Cambiar a True en producción
        samesite="Lax",
        path="/"            # Igual que arriba
    )

    return response


@router.get("/logout")
async def logout(request: Request):
    """
    Desautentica al usuario eliminando los cookies de 'user_id' y 'access_token'.

    Esta ruta responde con un redireccionamiento a la pagina principal ("/").
    El cliente debe reautenticarse para acceder a recursos protegidos.

    Args:
        request (Request): El objeto de solicitud HTTP que contiene los encabezados y cookies.

    Returns:
        RedirectResponse: Un redireccionamiento HTTP 302 con la cabecera 'Location' establecida a "/".
    """
    token = request.cookies.get("user_id")

    response = RedirectResponse("/", status_code=status.HTTP_302_FOUND)

    response.delete_cookie("user_id", path="/")
    response.delete_cookie("access_token", path="/")
    return response



@router.post("/create_usuario", response_model=UsuarioPublic)
async def crear(data: UserTable, session: SessionDep):
    password_hash = UsuarioCreate(nombre_apellido=data.nombre_apellido,
                                  email=data.email,rol=data.rol,activo=data.activo,
                                  codigo=data.codigo,regional=data.regional,
                                  regional_comision=data.regional_comision,
                                  password=get_password_hass(data.password))
    create_db = await create_registro(data=password_hash, session=session)
    return create_db




@router.get("/consulta_usuario/{registro_id}", response_model=UsuarioPublic)
async def obtener(registro_id: int, session: SessionDep):
    registro = await get_registro(session, registro_id)
    if not registro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro no encontrado")
    return JSONResponse(content=jsonable_encoder(registro))


@router.get("/lista_usuarios", response_model=list[UsuarioRead])
async def listar(session: SessionDep, limit: int = 100, offset: int = 0):
    lista = await get_registros(session, limit, offset)
    return JSONResponse(content=jsonable_encoder(lista))


@router.patch("/actualizacion_usuarios/{registro_id}", response_model=UsuarioPublic)
async def actualizar(session: SessionDep, registro_id: int, data: UsuarioUpdate):
    registro_udate = UsuarioUpdate(nombre_apellido=data.nombre_apellido,
                                   email=data.email,rol=data.rol,
                                   password=get_password_hass(data.password))

    registro = await update_registro(session, registro_id, registro_udate)
    if not registro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro no encontrado")
    return registro


@router.delete("/borrar_usuarios/{registro_id}")
async def eliminar(registro_id: int, session: SessionDep):
    registro = await delete_registro(session, registro_id)
    if not registro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro no encontrado")