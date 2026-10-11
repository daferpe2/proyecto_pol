from sqlmodel import select  # noqa: N999

from db import SessionDep
from models import (
    UserTable,
    UsuarioCreate,
    UsuarioUpdate,
)


async def create_registro(data: UsuarioCreate, session: SessionDep):
    data_c = data.model_dump()
    registro = UserTable.model_validate(data_c)
    session.add(registro)
    session.commit()
    session.refresh(registro)
    return registro


async def get_registro(session: SessionDep, registro_id: int):
    return session.get(UserTable, registro_id)


async def get_registros(session: SessionDep, limit: int = 100, offset: int = 0):
    query = select(UserTable).offset(offset).limit(limit)
    return session.exec(query).all()


async def update_registro(session: SessionDep, registro_id: int, data: UsuarioUpdate):
    registro = session.get(UserTable, registro_id)
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
    registro = session.get(UserTable, registro_id)
    if not registro:
        return None

    session.delete(registro)
    session.commit()
    return registro