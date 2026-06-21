from fastapi import FastAPI
from pydantic import BaseModel, Field
from datetime import datetime
import csv
import os
import pytz
import time

app = FastAPI()

class SensorData(BaseModel):
    temperatura: float = Field(..., ge=-50, le=100)
    humedad: float = Field(..., ge=0, le=100)

# Especifica la ruta completa al volumen montado
CSV_FILE = "/app/sensor_data/datos_sensor.csv"

# Crear el archivo si no existe
if not os.path.exists(CSV_FILE):
    os.makedirs(os.path.dirname(CSV_FILE), exist_ok=True)  # Asegurarse de que el directorio exista
    with open(CSV_FILE, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "temperatura", "humedad"])

def rotate_csv_if_needed():
    MAX_SIZE = 10 * 1024 * 1024  # 10 MB
    if os.path.exists(CSV_FILE) and os.path.getsize(CSV_FILE) > MAX_SIZE:
        ts = time.strftime("%Y%m%d_%H%M%S")
        rotated = f"{CSV_FILE}.{ts}"
        os.rename(CSV_FILE, rotated)
        with open(CSV_FILE, mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "temperatura", "humedad"])
        print(f"[INFO] CSV rotated: {rotated}")

@app.post("/api/sensor-data")
async def recibir_datos(data: SensorData):
    rotate_csv_if_needed()
    chile_timezone = pytz.timezone('Chile/Continental')
    timestamp = datetime.now(chile_timezone).isoformat()
    
    with open(CSV_FILE, mode="a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, data.temperatura, data.humedad])
    print(f"[{timestamp}] Temp: {data.temperatura} °C | Hum: {data.humedad} %")
    return {"status": "ok", "timestamp": timestamp}
