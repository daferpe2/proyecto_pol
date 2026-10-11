
from sqlmodel import select

from db import SessionDep
from models import PdpPoligrafistasTabla, TablaBaseEspF


async def busqueda_esp(db: SessionDep,texto_busqueda):
    resultado = db.exec(
        select(TablaBaseEspF).where(TablaBaseEspF.texto_busqueda.ilike(f"%{texto_busqueda}%"))).all()
    return resultado

async def busqueda_rdp(db: SessionDep,texto_busqueda):
    resultado = db.exec(
        select(PdpPoligrafistasTabla)
        .where(PdpPoligrafistasTabla.texto_busqueda.ilike(f"%{texto_busqueda}%"))
    ).all()
    return resultado

