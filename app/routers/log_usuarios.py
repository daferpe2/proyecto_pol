import base64
import json

from fastapi import APIRouter, HTTPException, Request, Depends,status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from app.operations.checkroles import check_roles
from app.operations.crud_usuarios import create_registro, delete_registro, get_registro, get_registros, update_registro
from app.operations.encryptedpayload import AES_KEY, EncryptedPayload
from db import SessionDep
from models import UsuarioCreate,UserTable, UsuarioPublic, UsuarioUpdate
from app.operations.autentiacion_funciones import get_current_user_id
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from password import get_password_hass


router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/create")
async def usuario_create_form(request: Request,
                              session: SessionDep,
                              user: UserTable = Depends(get_current_user_id)):
    if user is None:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse(
        "usuario_create.html",
        {"request": request,
         "user":user,
         "title":"Creación de Usuarios"}
    )


@router.post("/create_user")
async def create_usuario(
    db: SessionDep,
    data: EncryptedPayload,
    user: UserTable = Depends(get_current_user_id)
):
    """
    Recibe JSON cifrado desde el formulario,
    lo descifra y crea un nuevo usuario en la base de datos.
    """

    # Validación de usuario autenticado
    if not isinstance(user, UserTable):
        return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)

    # Inicializar AES
    aesgcm = AESGCM(AES_KEY)

    # Decodificar IV y payload
    iv = base64.b64decode(data.iv)
    payload = base64.b64decode(data.payload)

    # Descifrar
    decrypted_bytes = aesgcm.decrypt(iv, payload, None)
    decrypted_json = decrypted_bytes.decode("utf-8")

    # Convertir JSON → dict
    fields = json.loads(decrypted_json)
    fields["password"] = get_password_hass(fields["password"])

    # Convertir dict → modelo Pydantic
    usuario_obj = UsuarioCreate(**fields)

    # Insertar en BD
    create_db = await create_registro(data=usuario_obj, session=db)

    return {"mensaje":"Usuario Creado"}


@router.get("/editar_usuario/{id}")
async def get_update_resultados_esp(
    id: int,
    request: Request,
    session: SessionDep,
    user: UserTable = Depends(get_current_user_id)
):
    if not isinstance(user,UserTable):
        return RedirectResponse("/",status_code=status.HTTP_302_FOUND)
    
    check_roles(user)
    
    resultado = await get_registro(session,id)

    if not resultado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro no encontrado")
    print(resultado)
    return templates.TemplateResponse(
        "usuario_update.html",
        {
            "user":user,
            "request": request,
            "modo": "update",
            "registro": resultado,
        },
    )


@router.post("/update/{id}")
async def post_update_usuarios(
    id: int,
    data: EncryptedPayload,
    session: SessionDep,
    user: UserTable = Depends(get_current_user_id)
):
    if not isinstance(user, UserTable):
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

    aesgcm = AESGCM(AES_KEY)

    iv = base64.b64decode(data.iv)
    payload = base64.b64decode(data.payload)

    try:
        decrypted_bytes = aesgcm.decrypt(iv, payload, None)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error al descifrar datos")

    decrypted_json = decrypted_bytes.decode("utf-8")
    fields = json.loads(decrypted_json)

    # Manejo correcto del password
    if fields.get("password"):
        fields["password"] = get_password_hass(fields["password"])
    else:
        fields.pop("password", None)

    update_data = UsuarioUpdate(**fields)

    updated = await update_registro(session=session, registro_id=id, data=update_data)

    if not updated:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return {"message": "Registro actualizado correctamente"}




@router.get("/lista_usuarios", response_model=list[UsuarioPublic])
async def listar(request:Request,
                 session: SessionDep,
                 limit: int = 10, 
                 offset: int = 0,
                 user: UserTable = Depends(get_current_user_id)):


    if not isinstance(user,UserTable):
        return RedirectResponse("/",status_code=status.HTTP_302_FOUND)

    check_roles(user)

    registros = await get_registros(session, limit, offset)
    if not registros:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No se encontró el registro")
        


    return templates.TemplateResponse(
        "lista_usuarios.html",
        {
            "user":user,
            "request": request,
            "registros": registros,
            "limit": limit,
            "offset": offset, 
        }
    )





@router.post("/eliminar_usuario/{registro_id}")
async def eliminar(registro_id: int, session: SessionDep,
                   user: UserTable = Depends(get_current_user_id)):

    if not isinstance(user,UserTable):
        return RedirectResponse("/",status_code=status.HTTP_302_FOUND)
    
    check_roles(user) 
    
    registro = await get_registro(session,registro_id)

    if not registro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro no encontrado")
    await delete_registro(session, registro_id)

    return RedirectResponse("/usuarios/lista_usuarios",status_code=status.HTTP_303_SEE_OTHER)