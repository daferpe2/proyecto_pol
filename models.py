from datetime import UTC, date, datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, field_validator
from sqlmodel import Field, SQLModel

from app.operations.generacion_documento import numero_documento


def fechactual():
    return datetime.now().isoformat()

class EstadosValidacion(str,Enum):
    PENDIENTE = "Pendiente"
    OBSERVADO = "Observado"
    APROBADO = "Aprobado"
    RECHAZADO = "Rechazado"

# Usuarios

class Rol(str,Enum):
    registro="REGISTRO"
    qc = "QC"
    qc_s = "QC_S"
    analista = "ANALISTA"
    super_admin = "SUPER_ADMIN"
    jefe = "JEFE"
    coordinador = "COORDINADOR"


class Usuario(SQLModel):
    nombre_apellido: str = Field(default=None,index=True)
    email: EmailStr = Field(default=None,index=True)
    rol: str = Field(default=Rol.registro)
    activo: bool = Field(default=True)
    codigo: str = Field(default=None)
    password: str = Field(nullable=False, max_length=255)
    regional: str = Field(default=None)
    regional_comision: str = Field(default=None)


class UsuarioCreate(Usuario):
    nombre_apellido: str | None = "Pedro Perez"
    email: EmailStr | None = "Pedro_Perez@example.com"
    rol: Rol | None
    activo: bool | None = True
    codigo: str | None = "AIN-123"
    password: str | None
    regional: str | None
    regional_comision: str | None



class UsuarioUpdate(Usuario):
    nombre_apellido: str | None = None
    email: EmailStr | None = None
    rol: Rol | None = None
    activo: bool | None = True
    codigo: str | None = None
    password: str | None = None
    regional: str | None = None
    regional_comision: str | None = None


class UserTable(Usuario, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    fecha_creacion: date = Field(default_factory=date.today)

    # Correcto: 'list["TablaBaseEspF"]'
    # esp: Optional["TablaBaseEspF"] = Relationship(back_populates="lista_esp")



class UsuarioPublic(Usuario):
    id: int 

class UsuarioRead(Usuario):
    id: int


# TablaEsp


class TablaBaseEsp(SQLModel):
    fecha_asp: date | None = Field(default=None)
    proceso: str | None = Field(default=None)
    fuerza_jefatura: str | None = Field(default=None)
    comando_direccion_brigada_flotilla_grupo: str | None = Field(default=None)
    batallon_buque_unidad_labora: str | None = Field(default=None)
    no_cedula: str | None = Field(default=None)
    clase: str | None = Field(default=None)
    grado: str | None = Field(default=None)
    apellidos_nombre: str | None = Field(default=None)
    cargo: str | None = Field(default=None)
    resultados_obtenidos: str | None = Field(default=None)
    tipo_hallazgo: str | None = Field(default=None)
    observacion: str | None = Field(default=None)
    texto_busqueda: str | None = Field(default=None, index=True)
    regional: str | None = Field(default=None)

    @field_validator("texto_busqueda", mode="before")
    @classmethod
    def build_searchvector(cls, value, info):
        no_cedula = info.data.get("no_cedula") or ""
        apellidos_nombre = info.data.get("apellidos_nombre") or ""
        return f"{no_cedula} {apellidos_nombre}"


class TablaBaseEspF(TablaBaseEsp, table=True):
    id: int | None = Field(default=None, primary_key=True)

    fecha_registro: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )

    lista_esp_id: int | None = Field(default=None, foreign_key="usertable.id")
    numer_registro: str = Field(default_factory=numero_documento)

    fecha_act: date | None = Field(default=None)



class TablaBaseEspPublic(TablaBaseEsp):
    id: int


class CreacionEsp(TablaBaseEsp):
    fecha_asp: date | None
    proceso: str 
    fuerza_jefatura: str
    comando_direccion_brigada_flotilla_grupo: str 
    batallon_buque_unidad_labora: str 
    no_cedula: str 
    clase: str 
    grado: str 
    apellidos_nombre: str 
    cargo: str  
    resultados_obtenidos: str 
    tipo_hallazgo: str 
    observacion: str
    lista_esp_id : int | None
    regional: str | None


class TablaBaseEspUpdate(SQLModel):
    fecha_asp: date | None = None
    proceso: str | None = None
    fuerza_jefatura: str | None = None
    comando_direccion_brigada_flotilla_grupo: str | None = None
    batallon_buque_unidad_labora: str | None = None
    no_cedula: str | None = None
    clase: str | None = None
    grado: str | None = None
    apellidos_nombre: str | None = None
    cargo: str | None = None
    resultados_obtenidos: str | None = None
    tipo_hallazgo: str | None = None
    observacion: str | None = None
    texto_busqueda: str | None = None
    lista_esp_id: int | None = None
    fecha_act: date | None = date.today()
    regional: str | None = None
    texto_busqueda: str | None = None


class TablaBaseEspRead(TablaBaseEsp):
    id: int 


# ----------- 
# Nuevo Formulario PdpPoligrafistas


class PdpPoligrafistas(SQLModel):
    fecha_evaluacion: date | None = Field(default=None)
    regional: str | None = Field(default=None)
    categoria: str | None = Field(default=None)
    proceso: str | None = Field(default=None)
    complemento_proceso: str | None = Field(default=None)
    temas_examinados: str | None = Field(default=None)
    tecnica: str | None = Field(default=None)
    fuerza_jefatura: str | None = Field(default=None)
    comando_direccion_brigada_flotilla_grupo: str | None = Field(default=None)
    batallon_buque_unidad_labora: str | None = Field(default=None)
    no_cedula: str | None = Field(default=None)
    clase: str | None = Field(default=None)
    grado: str | None = Field(default=None)
    apellidos_nombres: str | None = Field(default=None)
    cargo: str | None = Field(default=None)
    resultado_epp: str | None = Field(default=None)
    tema_sr_di: str | None = Field(default=None)
    informacion_obtenida: str | None = Field(default=None)
    informacion_relevante: str | None = Field(default=None)
    observaciones: str | None = Field(default=None)
    refiere_alguien: str | None = Field(default=None)
    se_realizo_test_consumo: bool | None = Field(default=False)
    resultado_tmd: str | None = Field(default=None)
    tipo_sustancia: str | None = Field(default=None)
    texto_busqueda: str | None = Field(default=None,index=True,exclude=True)
    ain: str | None = Field(default=None)
    

    @field_validator("texto_busqueda",mode="before")
    @classmethod
    def build_searchvector(cls,value,info):
        no_cedula = info.data.get("no_cedula") or ""
        apellidos_nombres = info.data.get("apellidos_nombres") or ""
        return f"{no_cedula} {apellidos_nombres}"



class PdpPoligrafistasTabla(PdpPoligrafistas, table=True):
    id: int | None = Field(default=None, primary_key=True)
    fecha_registro: datetime = Field(default_factory=datetime.now)
    fecha_act: date | None = Field(default=None)
    usuario: int | None = Field(default=None, foreign_key="usertable.id")
    estado: EstadosValidacion = Field(default=EstadosValidacion.PENDIENTE)






class PdpPoligrafistasTablaPublic(PdpPoligrafistas):
    id: int


class PdpPoligrafistasTablaPublicCreate(PdpPoligrafistas):
    fecha_evaluacion: date | None 
    regional: str 
    categoria: str 
    proceso: str 
    complemento_proceso: str 
    temas_examinados: str 
    tecnica: str 
    fuerza_jefatura: str
    comando_direccion_brigada_flotilla_grupo: str 
    batallon_buque_unidad_labora: str 
    no_cedula: str 
    clase: str 
    grado: str 
    apellidos_nombres: str 
    cargo: str 
    resultado_epp: str 
    tema_sr_di: str 
    informacion_obtenida: str     
    informacion_relevante: str 
    observaciones: str 
    refiere_alguien: str 
    se_realizo_test_consumo: bool | None
    resultado_tmd: str | None
    tipo_sustancia: str | None 
    ain: str | None
    usuario: int | None
    texto_busqueda: str | None 



class PdpPoligrafistasUpdate(SQLModel):
    fecha_evaluacion: date | None = None
    regional: str | None = None
    categoria: str | None = None
    proceso: str | None = None
    complemento_proceso: str | None = None
    temas_examinados: str | None = None
    tecnica: str | None = None
    fuerza_jefatura: str | None = None
    comando_direccion_brigada_flotilla_grupo: str | None = None
    batallon_buque_unidad_labora: str | None = None
    no_cedula: str | None = None
    clase: str | None = None
    grado: str | None = None
    apellidos_nombres: str | None = None
    cargo: str | None = None
    resultado_epp: str | None = None
    tema_sr_di: str | None = None
    informacion_obtenida: str | None = None
    informacion_relevante: str | None = None
    observaciones: str | None = None
    refiere_alguien: str | None = None
    se_realizo_test_consumo: bool | None = None
    resultado_tmd: str | None = None
    tipo_sustancia: str | None = None
    texto_busqueda: str | None = None
    fecha_act: datetime | None = None
    ain: str | None = None
    usuario: int | None = None
    estado: str | None = None


# BUSCADOR CSV

class JobEstado(str, Enum):
    PENDIENTE = "PENDIENTE"
    EN_PROCESO = "EN_PROCESO"
    COMPLETADO = "COMPLETADO"
    ERROR = "ERROR"
    INTERRUMPIDO = "INTERRUMPIDO"
    ERROR_GLOBAL = "ERROR_GLOBAL"


class BuscadorJob(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    usuario: str
    estado: JobEstado = Field(default=JobEstado.PENDIENTE)
    fecha_creacion: datetime = Field(default_factory=datetime.now)
    fecha_actualizacion: datetime = Field(default_factory=datetime.now)
    ruta_archivo_resultado: str | None = None
    error_detalle: str | None = None

# Modelos para validación



class RDPJob(SQLModel,table=True):
    id: int | None = Field(default=None, primary_key=True)
    usuario: str
    estado: JobEstado = Field(default=JobEstado.PENDIENTE)
    fecha_creacion: datetime = Field(default_factory=datetime.now)
    fecha_actualizacion: datetime = Field(default_factory=datetime.now)
    ruta_archivo_resultado: str | None = None
    error_detalle: str | None = None




# Validacion


# Validacion 

class RDPAuditoria(SQLModel,table=True):
    id: int | None = Field(default=None, primary_key=True)
    rdp_id: int | None = Field(default=None,foreign_key="pdppoligrafistastabla.id")
    auditor_id: int | None = Field(default=None,foreign_key="usertable.id")
    comentarios: str | None = Field(default=None)
    fecha: datetime = Field(default_factory=datetime.now)

class RDPAuditoriaCreate(RDPAuditoria):
    rdp_id: int | None
    auditor_id: int | None
    comentarios: str | None


class RDPAuditoriaUpdate(RDPAuditoria):
    rdp_id: int | None
    auditor_id: int | None
    comentarios: str | None



# Carga masiva

class JobCargaRDP(BaseModel):
    id: int
    usuario_id: int
    rol: str
    nombre_archivo: str
    estado: str
    fecha_creacion: datetime
    fecha_inicio: datetime | None
    fecha_fin: datetime | None
    total_filas: int | None
    filas_insertadas: int | None
    filas_con_error: int | None
    errores_json: list | None

