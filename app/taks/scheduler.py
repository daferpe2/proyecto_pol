from apscheduler.schedulers.asyncio import AsyncIOScheduler
import os
import shutil
from datetime import datetime

# Carpetas a borrar
TEMP_DIRS = [
    "temp",
    "results"
]

def borrar_carpeta(path: str):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path, exist_ok=True)

def tarea_limpieza():
    print(f"[{datetime.now()}] Ejecutando limpieza programada...")

    for carpeta in TEMP_DIRS:
        borrar_carpeta(carpeta)

    print("✔ Carpetas temporales borradas y recreadas.")

