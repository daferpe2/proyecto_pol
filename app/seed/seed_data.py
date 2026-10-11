import random
from datetime import date, datetime

from faker import Faker
from sqlmodel import Session

from app.db import engine
from app.models import (
    PdpPoligrafistasTabla,
    TablaBaseEspF,
    UserTable,
)
from password import get_password_hass

fake = Faker("es_CO")
Faker.seed(1234)

ROLES = ["REGISTRO", "QC", "QC_S", "ANLISTA", "SUPER_ADMIN", "JEFE"]
CODIGO = ["AIN-123","AIN-234","AIN-852"]
REGIONAL = ["DEPEC","RCICA","RCIPA","RCIAM","RCIOR"]

def generar_usuario():
    return UserTable(
        nombre_apellido=fake.name(),
        email=fake.unique.email(),
        rol=random.choice(ROLES),
        activo=True,
        codigo=random.choice(CODIGO),
        password=get_password_hass(fake.password(length=12)),
        fecha_creacion=date.today(),
        regional=random.choice(REGIONAL),
        regional_comision=random.choice(REGIONAL),
    )

def generar_esp(usuario_id: int):
    nombre = fake.name()
    cedula = fake.msisdn()[:10]

    return TablaBaseEspF(
        fecha_asp=fake.date_between(start_date="-2y", end_date="today"),
        proceso=random.choice(["INSPECCIÓN", "AUDITORÍA", "VERIFICACIÓN"]),
        fuerza_jefatura=random.choice(["COARC", "DIMAR", "ARC"]),
        comando_direccion_brigada_flotilla_grupo=fake.word().upper(),
        batallon_buque_unidad_labora=fake.word().upper(),
        no_cedula=cedula,
        clase=random.choice(["A", "B", "C"]),
        grado=random.choice(["I", "II", "III"]),
        apellidos_nombre=nombre,
        cargo=random.choice(["TÉCNICO", "INSPECTOR", "SUPERVISOR"]),
        resultados_obtenidos=fake.sentence(),
        tipo_hallazgo=random.choice(["POSITIVO", "NEGATIVO", "NEUTRO"]),
        observacion=fake.paragraph(),
        text_buscador=f"{cedula} {nombre}",
        fecha_registro=datetime.now(),
        lista_esp_id=usuario_id,
        numer_registro=fake.bothify("ESP-####-??"),
        fecha_act=None,
        regional=random.choice(REGIONAL)
    )


def generar_rdp(usuario: int):
    nombre = fake.name()
    cedula = fake.msisdn()[:10]

    return PdpPoligrafistasTabla(
        fecha_evaluacion=fake.date_between(start_date="-2y", end_date="today"),
        regional=random.choice(["RENIC","RECIF","RECOIF","RECISU"]),
        categoria=random.choice(["VULNERABILIDADES","PREZARPE","SELECCION"]),
        proceso=random.choice(["OP_ORION","OP_DIPLOMATICAS","OP_ENTRENAMIENTO"]),
        complemento_proceso=fake.sentence(),
        temas_examinados=fake.sentence(),
        fuerza_jefatura=random.choice(["COARC", "DIMAR", "ARC"]),
        comando_direccion_brigada_flotilla_grupo=fake.word().upper(),
        batallon_buque_unidad_labora=fake.word().upper(),
        no_cedula=cedula,
        clase=random.choice(["A", "B", "C"]),
        grado=random.choice(["A", "B", "C"]),
        apellidos_nombres=nombre,
        cargo=random.choice(["TÉCNICO", "INSPECTOR", "SUPERVISOR"]),
        resultado_epp=random.choice(["NSR","NDI","NPE"]),
        tema_sr_di=fake.word(),
        informacion_obtenida=fake.sentence(),
        informacion_relevante=fake.sentence(),
        observaciones=fake.sentence(),
        refiere_alguien=random.choice(["SI","NO"]),
        se_realizo_test_consumo=fake.boolean(),
        resultado_tmd=fake.sentence(),
        tipo_sustancia=fake.sentence(),
        ain=random.choice(CODIGO),
        usuario=usuario
    )


def run_seed(cant_usuarios=10, cant_esp=50):
    with Session(engine) as session:
        usuarios = []

        # Crear usuarios
        for _ in range(cant_usuarios):
            u = generar_usuario()
            session.add(u)
            session.commit()
            session.refresh(u)
            usuarios.append(u)

        # Crear ESP asociados
        for _ in range(cant_esp):
            usuario = random.choice(usuarios)
            esp = generar_esp(usuario.id)
            session.add(esp)

        session.commit()

        # Crear RDP asociados
        for _ in range(cant_esp):
            usuario = random.choice(usuarios).id  # ✔ CORREGIDO
            rdp = generar_rdp(usuario)
            session.add(rdp)

        session.commit()

    print("✔ Seed ejecutado correctamente")


if __name__ == "__main__":
    run_seed()
