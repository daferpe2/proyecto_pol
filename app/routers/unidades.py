# app/api/unidades.py
import csv
from fastapi import APIRouter

router = APIRouter()

@router.get("/unidades")
async def get_unidades():
    data = {}

    with open("app/static/data/unidades_csv.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            fuerza = row["fuerza_jefatura"]
            comando = row["comando_direccion_brigada_flotilla_grupo"]
            unidad = row["batallon_buque_unidad_labora"]

            if fuerza not in data:
                data[fuerza] = {}

            if comando not in data[fuerza]:
                data[fuerza][comando] = []

            data[fuerza][comando].append(unidad)

    return data


@router.get("/categorias")
async def get_categorias():
    data = {}

    with open("app/static/data/categorias.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            categoria = row["categorias"]
            proceso = row["proceso"]

            if categoria not in data:
                data[categoria] = []

            data[categoria].append(proceso)

    return data


@router.get("/grado_clase")
async def get_grado_clase():
    data = {}

    with open("app/static/data/grado_clase.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            categoria = row["clase"]
            proceso = row["grado"]

            if categoria not in data:
                data[categoria] = []

            data[categoria].append(proceso)

    return data
