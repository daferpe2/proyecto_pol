import base64
import json
from datetime import datetime

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.operations.autentiacion_funciones import get_current_user_id
from app.operations.checkroles import check_roles, require_role
from app.operations.crudEsp import (
    create_registro,
    delete_registro,
    get_registro,
    get_registros,
    get_registros_busqueda,
    update_registro,
)
from app.operations.encryptedpayload import AES_KEY, EncryptedPayload
from app.operations.keyset import keyset_query_esp
from db import SessionDep
from models import (
    CreacionEsp,
    Rol,
    TablaBaseEspF,
    TablaBaseEspPublic,
    TablaBaseEspUpdate,
    UserTable,
)

router = APIRouter(prefix="/tabla-base-esp", tags=["TablaBaseEsp"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/resultados-esp/form")
async def form_resultados_esp(
    request: Request,
    session: SessionDep,
    user: UserTable = Depends(get_current_user_id)
):

    if user is None:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse(
        "form_resultados_esp.html",
        {
            "request": request,
            "title": "Resultados Obtenidos ESP",
            "user": user
        }
    )

@router.post("/create_esp",response_model=TablaBaseEspPublic)
async def create_esp(session: SessionDep,
                     data: EncryptedPayload,
                     user: UserTable = Depends(get_current_user_id)):

    if not isinstance(user, UserTable):
        return RedirectResponse("/",status_code=status.HTTP_303_SEE_OTHER)

    aesgcm = AESGCM(AES_KEY)

    iv = base64.b64decode(data.iv)
    payload = base64.b64decode(data.payload)

    decrypted_bytes = aesgcm.decrypt(iv, payload, None)
    decrypted_json = decrypted_bytes.decode("utf-8")

    fields = json.loads(decrypted_json)
    objs = CreacionEsp(**fields)
    create_db = await create_registro(data=objs, session=session)
    return create_db


@router.get("/consulta_esp/{registro_id}", response_model=TablaBaseEspPublic)
async def obtener(registro_id: int, session: SessionDep,
                  user: UserTable = Depends(get_current_user_id)):

    if not isinstance(user, UserTable):
        return RedirectResponse("/",status_code=status.HTTP_303_SEE_OTHER)

    registro = await get_registro(session, registro_id)
    if not registro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro no encontrado")
    return JSONResponse(content=jsonable_encoder(registro))


@router.get("/lista_esp", response_model=list[TablaBaseEspPublic])
async def listar(request:Request,
                 session: SessionDep,
                 q: str | None = None,
                 limit: int = 5, 
                 offset: int = 0,
                 user: UserTable = Depends(get_current_user_id)):


    if not isinstance(user,UserTable):
        return RedirectResponse("/",status_code=status.HTTP_302_FOUND)

    check_roles(user)

    if q:
        registros = await get_registros_busqueda(q, session, limit, offset)
    else:
        registros = await get_registros(session, limit, offset)


    return templates.TemplateResponse(
        "resultados_poligraficos.html",
        {
            "user":user,
            "request": request,
            "registros": registros,
            "limit": limit,
            "offset": offset,
            "q": q or ""
        }
    )

@router.patch("/actualizacion_esp/{registro_id}", response_model=TablaBaseEspPublic)
async def actualizar(session: SessionDep, registro_id: int, data: TablaBaseEspUpdate,
                     user: UserTable = Depends(get_current_user_id)):
    
    if not isinstance(user,UserTable):
        return RedirectResponse("/",status_code=status.HTTP_302_FOUND)

    # check_roles(user)
    
    registro = await update_registro(session, registro_id, data)
    if not registro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro no encontrado")
    return registro


@router.post("/eliminar_poligrafico/{registro_id}")
async def eliminar(registro_id: int, session: SessionDep,
                   user: UserTable = Depends(get_current_user_id)):

    if not isinstance(user,UserTable):
        return RedirectResponse("/",status_code=status.HTTP_302_FOUND)
    
    # check_roles(user) 
    
    registro = await get_registro(session,registro_id)

    if not registro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro no encontrado")
    await delete_registro(session, registro_id)

    return RedirectResponse("/tabla-base-esp/lista_esp",status_code=status.HTTP_303_SEE_OTHER)



@router.post("/eliminar_poligrafico_regional/{registro_id}")
async def eliminar_regional(registro_id: int, session: SessionDep,
                   user: UserTable = Depends(get_current_user_id)):

    if not isinstance(user,UserTable):
        return RedirectResponse("/",status_code=status.HTTP_302_FOUND)
    
    require_role([Rol.qc])
    
    registro = await get_registro(session,registro_id)

    if not registro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro no encontrado")
    await delete_registro(session, registro_id)

    return RedirectResponse("/tabla-base-esp/lista_sdp_regional",status_code=status.HTTP_303_SEE_OTHER)



@router.get("/resultados_poligraficos")
async def resultados_poligraficos(request: Request, 
                                  session: SessionDep, 
                                  limit: int = 5, offset: int = 0,
                                  user: UserTable = Depends(get_current_user_id)):

    if not isinstance(user,UserTable):
        return RedirectResponse("/",status_code=status.HTTP_302_FOUND)

    resultados = await get_registros(session, limit, offset)

    return templates.TemplateResponse(
        "resultados_poligraficos.html",
        {
            "request": request,
            "resultados": resultados,
            "limit": limit,
            "offset": offset
        }
    )

# Actualización

@router.get("/editar_poligrafico/{id}")
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

    # if resultado.regional != user.regional:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro no encontrado")

    if not resultado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro no encontrado")
    print(resultado)
    return templates.TemplateResponse(
        "editar_poligrafico.html",
        {
            "user":user,
            "request": request,
            "modo": "update",
            "registro": resultado,
        },
    )


@router.post("/update/{id}")
async def post_update_resultados_esp(
    id: int,
    data: EncryptedPayload,
    session: SessionDep,
    user: UserTable = Depends(get_current_user_id)
):
    if not isinstance(user,UserTable):
        return RedirectResponse("/",status_code=status.HTTP_302_FOUND)
    # 1. Descifrar payload
    aesgcm = AESGCM(AES_KEY)

    iv = base64.b64decode(data.iv)
    payload = base64.b64decode(data.payload)

    try:
        decrypted_bytes = aesgcm.decrypt(iv, payload, None)
    except Exception:
        raise HTTPException(status_code=400, detail="Error al descifrar datos")

    decrypted_json = decrypted_bytes.decode("utf-8")
    fields = json.loads(decrypted_json)
    fields["texto_busqueda"] = f"{fields['no_cedula']} {fields['apellidos_nombre']}"

    # 2. Convertir a modelo de update
    update_data = TablaBaseEspUpdate(**fields)

    # 3. Obtener registro actual
    registro = await get_registro(session,id)

    if not registro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro no encontrado")

    # 4. Actualizar solo campos con valor (mantener anteriores si vienen vacíos)
    for field_name, value in update_data.model_dump().items():
        # saltar campos None
        if value is None:
            continue

        # si es string vacío, mantener valor anterior
        if isinstance(value, str) and value.strip() == "":
            continue

        setattr(registro, field_name, value)

    # 5. Actualizar fecha_registro como fecha de modificación (tu opción B)
    registro.fecha_act = datetime.now()
    registro.lista_esp_id = user.id

    # 6. Guardar cambios
    session.add(registro)
    session.commit()
    session.refresh(registro)

    return {"message": "Registro actualizado correctamente"}


# Consultas Regionales

@router.get("/lista_sdp_regional")
async def listar_regional(
    request: Request,
    session: SessionDep,
    last_id: int | None = None,
    limit: int = 5,
    direction: str = "next",
    user: UserTable = Depends(get_current_user_id)
):

    if not isinstance(user, UserTable):
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

    filters = [TablaBaseEspF.regional == user.regional]

    items, next_cursor, prev_cursor = keyset_query_esp(
    session=session,
    model=TablaBaseEspF,
    last_id=last_id,
    limit=limit,
    filters=filters,
    reverse=(direction == "prev"))

    # prev_cursor = primer ID de la página actual
    prev_cursor = items[0].id if items else None

    return templates.TemplateResponse(
        "resultados_esp_regionales.html",
        {
            "request": request,
            "user": user,
            "registros": items,
            "next_cursor": next_cursor,
            "prev_cursor": prev_cursor,
        }
    )


@router.get("/lista_esp_fragment")
async def lista_rdp_fragment(
    request: Request,
    session: SessionDep,
    last_id: int | None = None,
    limit: int = 5,
    direction: str = "next",
    user: UserTable = Depends(get_current_user_id)
):

    filters = [TablaBaseEspF.regional == user.regional]


    items, next_cursor, prev_cursor = keyset_query_esp(
    session=session,
    model=TablaBaseEspF,
    last_id=last_id,
    limit=limit,
    filters=filters,
    reverse=(direction == "prev")
    )

    return templates.TemplateResponse(
        "fragment_esp_cards.html",
        {
            "request": request,
            "registros": items,
            "next_cursor": next_cursor,
            "prev_cursor": prev_cursor,
            "user": user
        }
    )
