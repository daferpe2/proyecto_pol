from datetime import datetime, timedelta

from sqlmodel import and_, func, select # noqa: N999

from db import SessionDep
from models import (
    EstadosValidacion,
    PdpPoligrafistasTabla,
    PdpPoligrafistasTablaPublicCreate,
    PdpPoligrafistasUpdate,
)


async def create_registro(data: PdpPoligrafistasTablaPublicCreate, session: SessionDep):
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
    registro = PdpPoligrafistasTabla.model_validate(data_c)
    session.add(registro)
    session.commit()
    session.refresh(registro)
    return registro


async def get_registro(session: SessionDep, registro_id: int):
    """
    Obtiene un registro por su ID.

        .order_by(PdpPoligrafistasTabla.id.desc())
    Arg
        .order_by(PdpPoligrafistasTabla.id.desc())s
        .order_by(PdpPoligrafistasTabla.id.desc()):
        session (SessionDep):
            Sesión de base de datos activa.
        registro_id (int):
            Identificador único del registro a consultar.

    Returns:
        PdpPoligrafistasTabla | None:
            El registro encontrado o None si no existe.
    """
    return session.get(PdpPoligrafistasTabla, registro_id)


async def get_registros(
    session: SessionDep,
    limit: int = 100,
    offset: int = 0
):
    query = (
        select(PdpPoligrafistasTabla).where(PdpPoligrafistasTabla.estado==EstadosValidacion.PENDIENTE)
        .order_by(PdpPoligrafistasTabla.id.desc())
        .limit(limit)
        .offset(offset)
    )


    return session.exec(query).all()


async def get_registros_regional(
    regional: str,
    session: SessionDep,
    limit: int = 100,
    offset: int = 0
):
    query = (
        select(PdpPoligrafistasTabla).where(and_(
            PdpPoligrafistasTabla.estado==EstadosValidacion.PENDIENTE),
            PdpPoligrafistasTabla.regional==regional
        )            
        .order_by(PdpPoligrafistasTabla.id.desc())
        .limit(limit)
        .offset(offset)
    )


    return session.exec(query).all()


async def get_registros_busqueda(
    q: str | None,
    session: SessionDep,
    limit: int = 100,
    offset: int = 0
):
    query = (
        select(PdpPoligrafistasTabla)
        .order_by(PdpPoligrafistasTabla.id.desc())
        .where(PdpPoligrafistasTabla.texto_busqueda.ilike(f"%{q}%"))
        .limit(limit)
        .offset(offset)
    )

    return session.exec(query).all()

async def get_registros_busqueda_regional(
    q: str | None,
    regional: str,
    session: SessionDep,
    limit: int = 100,
    offset: int = 0
    ):
    
    query = (
    select(PdpPoligrafistasTabla).where(PdpPoligrafistasTabla.regional == regional)
    .order_by(PdpPoligrafistasTabla.id.desc())
    .where(PdpPoligrafistasTabla.texto_busqueda.ilike(f"%{q}%"))
    .limit(limit)
    .offset(offset)
)


    return session.exec(query).all()


async def update_registro(session: SessionDep, registro_id: int, data: PdpPoligrafistasUpdate):
    """
    Actualiza un registro existente.

    Solo se modifican los campos enviados en el esquema `PdpPoligrafistasUpdate`,
    ignorando aquellos no proporcionados (`exclude_unset=True`). Si el registro
    no existe, se retorna None.

    Args:
        session (SessionDep):
            Sesión de base de datos activa.
        registro_id (int):
            Identificador del registro a actualizar.
        data (PdpPoligrafistasUpdate):
            Datos a modificar en el registro.

    Returns:
        PdpPoligrafistasTabla | None:
            El registro actualizado o None si no existe.
    """
    registro = session.get(PdpPoligrafistasTabla, registro_id)
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

    Si el registro no existe, se retorna None. Si existe, se elimina de la base
    de datos y se retorna el objeto eliminado.

    Args:
        session (SessionDep):
            Sesión de base de datos activa.
        registro_id (int):
            Identificador del registro a eliminar.

    Returns:
        PdpPoligrafistasTabla | None:
            El registro eliminado o None si no existe.
    """
    registro = session.get(PdpPoligrafistasTabla, registro_id)
    if not registro:
        return None

    session.delete(registro)
    session.commit()
    return registro


async def  get_count_rdp_validacion(
        session: SessionDep
):
    conteo_pendientes = session.exec(select(func.count(PdpPoligrafistasTabla.estado)).where(
        PdpPoligrafistasTabla.estado == EstadosValidacion.PENDIENTE)
    ).one()

    conteo_aprobado = session.exec(select(func.count(PdpPoligrafistasTabla.estado)).where(
        PdpPoligrafistasTabla.estado == EstadosValidacion.APROBADO)
    ).one()

    return (conteo_pendientes,conteo_aprobado)


async def get_count_rdp_validacion_semana(
    session: SessionDep):

    hace_una_semana = datetime.now() - timedelta(days=7)

    conteo_pendientes_semana = session.exec(
        select(func.count()).where(and_(
            PdpPoligrafistasTabla.estado == EstadosValidacion.PENDIENTE,
            PdpPoligrafistasTabla.fecha_registro >= hace_una_semana))).one()

    return conteo_pendientes_semana


async def  get_count_rdp_validacion_regional(
        session: SessionDep,
        regional: str
):
    conteo_pendientes = session.exec(
    select(func.count()).where(
        and_(
            PdpPoligrafistasTabla.estado == EstadosValidacion.PENDIENTE,
            PdpPoligrafistasTabla.regional == regional
        )
    )
    ).one()

    conteo_aprobado = session.exec(select(func.count()).where(
        and_(
        PdpPoligrafistasTabla.estado == EstadosValidacion.APROBADO,
        PdpPoligrafistasTabla.regional == regional)
        )
    ).one()

    return (conteo_pendientes,conteo_aprobado)

async def get_count_rdp_validacion_semana_reginal(session: SessionDep, regional: str):

    hace_una_semana = datetime.now() - timedelta(days=7)

    conteo = session.exec(
        select(func.count()).where(and_(
            PdpPoligrafistasTabla.estado == EstadosValidacion.PENDIENTE,
            PdpPoligrafistasTabla.regional == regional,
            PdpPoligrafistasTabla.fecha_registro >= hace_una_semana))).one()

    return conteo