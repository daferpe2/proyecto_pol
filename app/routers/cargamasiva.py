from fastapi import APIRouter, File, Request, UploadFile
from fastapi import Depends, status,Response
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.operations.autentiacion_funciones import get_current_user_id
from app.operations.motor.bulk_inserter import BulkInserter
from app.operations.motor.excel_reader import ExcelReader
from app.operations.motor.load_config import LoadConfig
from app.operations.motor.load_orchestrator import LoadOrchestrator
from app.operations.motor.row_separator import RowSeparator
from app.operations.motor.row_transformer import RowTransformer
from app.operations.motor.row_validator import RowValidator
from app.operations.schemas.schemas_espf import schema_tabla_base_espf
from app.operations.schemas.schemas_poli import schema_pdp_poligrafistas
from db import SessionDep
from models import PdpPoligrafistasTabla, TablaBaseEspF, UserTable

router = APIRouter(prefix="/carga",tags=["CargaMasiva"])

templates = Jinja2Templates(directory="app/templates")

# Configuración de tablas
schemas = {
    "poli": {
        "expected_columns": schema_pdp_poligrafistas["expected_columns"],
        "schema": schema_pdp_poligrafistas["schema"],
        "transformer": RowTransformer()
    },
    "espf": {
        "expected_columns": schema_tabla_base_espf["expected_columns"],
        "schema": schema_tabla_base_espf["schema"],
        "transformer": RowTransformer()
    }
}

models = {
    "poli": PdpPoligrafistasTabla,
    "espf": TablaBaseEspF
}

load_config = LoadConfig(schemas, models)


@router.post("/upload/{table_name}")
async def cargar_excel(
    session: SessionDep,
    table_name: str,
    archivo: UploadFile = File(...),
    usuario_id: int = 1  # ejemplo
):
    config = load_config.get_config(table_name)

    motor = LoadOrchestrator(
        excel_reader=ExcelReader(),
        validator=RowValidator(),
        separator=RowSeparator(),
        transformer=config["transformer"],
        inserter=BulkInserter()
    )

    contenido = await archivo.read()

    context = {
        "usuario_id": usuario_id,
        "lista_esp_id": usuario_id  # si aplica
    }

    resultado = motor.run(
        file=contenido,
        config=config,
        context=context,
        session=session
    )

    return resultado






@router.get("/upload-form")
async def form_upload(
    request: Request,
    session: SessionDep,
    user: UserTable = Depends(get_current_user_id)
):

    if user is None:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse(
        "upload_form.html",
        {
            "request": request,
            "title": "Resultados Obtenidos ESP",
            "user": user
        }
    )