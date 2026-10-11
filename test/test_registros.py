import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.operations.crudPoligraf import (
    PdpPoligrafistasTablaPublicCreate,
    PdpPoligrafistasUpdate,
    create_registro,
    delete_registro,
    get_registro,
    get_registros,
    update_registro,
)

# -------------------------------------------------------------------
# FIXTURES
# -------------------------------------------------------------------

@pytest.fixture
def engine():
    """
    Crea una base de datos SQLite en memoria para pruebas.
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(engine):
    """
    Sesión de base de datos para cada test.
    """
    with Session(engine) as session:
        yield session


# -------------------------------------------------------------------
# TESTS
# -------------------------------------------------------------------

@pytest.mark.anyio
async def test_create_registro(session):
    data = PdpPoligrafistasTablaPublicCreate(
        nombre="Juan Pérez",
        documento="123456",
        activo=True
    )

    registro = await create_registro(data, session)

    assert registro.id is not None
    assert registro.nombre == "Juan Pérez"
    assert registro.documento == "123456"
    assert registro.activo is True


@pytest.mark.anyio
async def test_get_registro(session):
    # Crear registro primero
    data = PdpPoligrafistasTablaPublicCreate(
        nombre="Ana Gómez",
        documento="987654",
        activo=False
    )
    creado = await create_registro(data, session)

    obtenido = await get_registro(session, creado.id)

    assert obtenido is not None
    assert obtenido.id == creado.id
    assert obtenido.nombre == "Ana Gómez"


@pytest.mark.anyio
async def test_get_registros(session):
    # Crear varios registros
    for i in range(5):
        data = PdpPoligrafistasTablaPublicCreate(
            nombre=f"Persona {i}",
            documento=str(1000 + i),
            activo=True
        )
        await create_registro(data, session)

    registros = await get_registros(session, limit=5, offset=0)

    assert len(registros) == 5
    assert registros[0].nombre == "Persona 0"


@pytest.mark.anyio
async def test_update_registro(session):
    data = PdpPoligrafistasTablaPublicCreate(
        nombre="Carlos Ruiz",
        documento="555555",
        activo=True
    )
    creado = await create_registro(data, session)

    update_data = PdpPoligrafistasUpdate(
        nombre="Carlos Actualizado",
        activo=False
    )

    actualizado = await update_registro(session, creado.id, update_data)

    assert actualizado.nombre == "Carlos Actualizado"
    assert actualizado.activo is False


@pytest.mark.anyio
async def test_update_registro_not_found(session):
    update_data = PdpPoligrafistasUpdate(nombre="No existe")
    resultado = await update_registro(session, 999, update_data)

    assert resultado is None


@pytest.mark.anyio
async def test_delete_registro(session):
    data = PdpPoligrafistasTablaPublicCreate(
        nombre="Eliminar",
        documento="000000",
        activo=True
    )
    creado = await create_registro(data, session)

    eliminado = await delete_registro(session, creado.id)

    assert eliminado is not None
    assert eliminado.id == creado.id

    # Verificar que ya no existe
    assert await get_registro(session, creado.id) is None


@pytest.mark.anyio
async def test_delete_registro_not_found(session):
    resultado = await delete_registro(session, 999)
    assert resultado is None
