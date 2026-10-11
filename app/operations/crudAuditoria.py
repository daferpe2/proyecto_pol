from sqlmodel import select  # noqa: N999

from db import SessionDep
from models import RDPAuditoria, RDPAuditoriaCreate, RDPAuditoriaUpdate


async def create_registro_auditoria(data: RDPAuditoriaCreate, session: SessionDep):
    data_c = data.model_dump()
    registro = RDPAuditoria.model_validate(data_c)
    session.add(registro)
    session.commit()
    session.refresh(registro)
    return registro


async def get_registro_rdp(session: SessionDep, registro_id: int):

    return session.get(RDPAuditoria, registro_id)

# async def get_registros(session: SessionDep, id: int):
#     query = (
#     select(RDPAuditoria).where(RDPAuditoria.id == id)
#     )
#     return session.exec(query).all()


async def update_registro(session: SessionDep, 
                          registro_id: int, 
                          data: RDPAuditoriaUpdate):


    registro = session.get(RDPAuditoria, registro_id)
    if not registro:
        return None

    update_data = data.model_dump(exclude_unset=True).items()
    for key, value in update_data:
        setattr(registro, key, value)

    session.add(registro)
    session.commit()
    session.refresh(registro)
    return registro


async def delete_registro(session: SessionDep, registro_id: int):

    registro = session.get(RDPAuditoria, registro_id)
    if not registro:
        return None

    session.delete(registro)
    session.commit()
    return registro


async def get_registros_rdp(
    session: SessionDep,
    limit: int = 10,
    offset: int = 0
):
    query = (
    select(RDPAuditoria)
    .order_by(RDPAuditoria.fecha.desc())
    .offset(offset)
    .limit(limit))
    return session.exec(query).all()


