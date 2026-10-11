from sqlmodel import select  # noqa: N999

from db import SessionDep
from models import (
    CreacionEsp,
    TablaBaseEsp,
    TablaBaseEspF,
    TablaBaseEspUpdate,
)



async def create_registro(data: CreacionEsp, session: SessionDep):
    """
    Crea un nuevo registro en la tabla `PdpPoligrafistasTabla`.

    Este método toma los datos del esquema de creación, los convierte en un
    diccionario mediante `model_dump()`, valida el contenido contra el modelo
    SQLModel correspondiente y persiste el registro en la base de datos.

    Args:
        data (PdpPoligrafistasTablaPublicCreate):
            Datos necesarios para crear el registro.
        session (SessionDep):
            Sesión de base de datos inyectada mediante dependencia.

    Returns:
        PdpPoligrafistasTabla:
            El registro recién creado, incluyendo campos generados por la BD.
    """
    data_c = data.model_dump()
    registro = TablaBaseEspF.model_validate(data_c)
    session.add(registro)
    session.commit()
    session.refresh(registro)
    return registro




async def get_registro(session: SessionDep, registro_id: int):
    """
    Obtiene un registro específico por su ID.

    Args:
        session (SessionDep):
            Sesión de base de datos activa.
        registro_id (int):
            Identificador único del registro a consultar.

    Returns:
        TablaBaseEspCreate | None:
            El registro encontrado o None si no existe.
    """
    return session.get(TablaBaseEspF, registro_id)


async def get_registros(session: SessionDep, limit: int = 100, offset: int = 0):
    query = (
    select(TablaBaseEspF)
    .order_by(TablaBaseEspF.id.desc())
    .offset(offset)
    .limit(limit))
    return session.exec(query).all()


async def update_registro(session: SessionDep, registro_id: int, data: TablaBaseEspUpdate):
    """
    Actualiza un registro existente.

    El método obtiene el registro por ID, aplica únicamente los campos
    proporcionados (excluyendo los no enviados mediante `exclude_unset=True`)
    y guarda los cambios en la base de datos.

    Args:
        session (SessionDep):
            Sesión de base de datos activa.
        registro_id (int):
            Identificador del registro a actualizar.
        data (TablaBaseEspUpdate):
            Datos a modificar en el registro.

    Returns:
        TablaBaseEspCreate | None:
            El registro actualizado o None si no existe.
    """
    registro = session.get(TablaBaseEspF, registro_id)
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
    """
    Elimina un registro por su ID.

    Args:
        session (SessionDep):
            Sesión de base de datos activa.
        registro_id (int):
            Identificador del registro a eliminar.

    Returns:
        TablaBaseEspCreate | None:
            El registro eliminado o None si no existe.
    """
    registro = session.get(TablaBaseEspF, registro_id)
    if not registro:
        return None

    session.delete(registro)
    session.commit()
    return registro


async def get_registros_busqueda(
    q: str | None,
    session: SessionDep,
    limit: int = 100,
    offset: int = 0
):
    query = (
        select(TablaBaseEspF)
        .where(TablaBaseEspF.texto_busqueda.ilike(f"%{q}%"))
        .limit(limit)
        .offset(offset)
    )

    return session.exec(query).all()


