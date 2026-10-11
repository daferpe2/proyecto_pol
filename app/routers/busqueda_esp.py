# rutas/resultados_poligraficos.py

import os
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, Form, Request, status
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import select

from app.operations.access_token import access_token_m
from app.operations.autentiacion_funciones import get_current_user_id
from app.operations.busqueda import busqueda_esp, busqueda_rdp
from app.operations.checkroles import check_roles
from app.operations.informe_depec import InformeDEPEC, InformeRDP
from db import SessionDep
from models import (
    PdpPoligrafistasTabla,
    TablaBaseEspF,
    UserTable,
)

router = APIRouter(prefix="/resultados-poligraficos", tags=["Resultados Poligráficos"])

templates = Jinja2Templates(directory="app/templates")

# ---------------------------
# 1. GET - Página del buscador
# ---------------------------
@router.get("/buscar")
async def buscador_page(request: Request, user: UserTable= Depends(get_current_user_id)):

    if not isinstance(user, UserTable):
        return RedirectResponse("/",status_code=status.HTTP_303_SEE_OTHER)

    check_roles(user=user)

    return templates.TemplateResponse(
        "buscador_resultados.html",
        {"request": request, "resultados": None,
         "user":user}
    )


# ---------------------------
# 2. POST - Ejecutar búsqueda
# ---------------------------
@router.post("/buscar")
async def ejecutar_busqueda(
    db: SessionDep,
    request: Request,
    texto_busqueda: str = Form(...),
    user: UserTable = Depends(get_current_user_id),
    access_token: Annotated[str | None, Cookie()] = None
):
    access_token_m(access_token)

    check_roles(user=user)

    resultados_rdp = await busqueda_rdp(db=db,texto_busqueda=texto_busqueda)
    resultados_esp = await busqueda_esp(db=db,texto_busqueda=texto_busqueda)

    return templates.TemplateResponse(
        "buscador_resultados.html",
        {
            "user":user,
            "request": request,
            "resultados_esp": resultados_esp,
            "resultados_rdp": resultados_rdp,
            "texto_busqueda": texto_busqueda
        }
    )


@router.post("/generar-informe-depec")
async def generar_informe_depec(
    request: Request,
    db: SessionDep,
    user = Depends(get_current_user_id),
    access_token: Annotated[str | None, Cookie()] = None
):

    if not isinstance(user, UserTable):
        return RedirectResponse("/",status_code=status.HTTP_303_SEE_OTHER)

    access_token_m(access_token)

    check_roles(user=user)

    os.makedirs("temp", exist_ok=True)

    body = await request.json()
    ids = body.get("ids", [])  # lista de IDs seleccionados en el buscador

    registros = db.exec(select(TablaBaseEspF).where(TablaBaseEspF.id.in_(ids))).all()

    informe = InformeDEPEC(registros=registros, usuario=user)
    filepath = informe.exportar()

    return FileResponse(
        filepath,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=os.path.basename(filepath),
    )


@router.post("/generar-informe-rdp")
async def generar_informe_rdp(
    request: Request,
    db: SessionDep,
    user = Depends(get_current_user_id),
    access_token: Annotated[str | None, Cookie()] = None
):
    access_token_m(access_token)

    if not isinstance(user, UserTable):
        return RedirectResponse("/",status_code=status.HTTP_303_SEE_OTHER)

    check_roles(user=user)

    os.makedirs("temp", exist_ok=True)

    body = await request.json()
    ids = body.get("ids", [])  # lista de IDs seleccionados en el buscador

    print(ids)

    registros = db.exec(select(PdpPoligrafistasTabla).where(PdpPoligrafistasTabla.id.in_(ids))).all()

    informe = InformeRDP(registros=registros, usuario=user)
    filepath = informe.exportar()

    return FileResponse(
        filepath,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=os.path.basename(filepath),
    )





