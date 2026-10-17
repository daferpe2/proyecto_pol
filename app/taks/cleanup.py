import os
import shutil
import asyncio
from datetime import datetime

TEMP_DIRS = [
    "temp",
    "results"
]

def borrar_carpeta(path: str):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path, exist_ok=True)

async def tarea_borrado_semanal():
    while True:
        print(f"[{datetime.now()}] Ejecutando limpieza semanal...")

        for carpeta in TEMP_DIRS:
            borrar_carpeta(carpeta)

        print("✔ Carpetas temporales borradas y recreadas.")

        # await asyncio.sleep(60)
        await asyncio.sleep(7 * 24 * 60 * 60)
