from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import csv
import os
import pytz

app = FastAPI()

class SensorData(BaseModel):
    temperatura: float
    humedad: float

# Especifica la ruta completa al volumen montado
CSV_FILE = "/app/sensor_data/datos_sensor.csv"

# Crear el archivo si no existe
if not os.path.exists(CSV_FILE):
    os.makedirs(os.path.dirname(CSV_FILE), exist_ok=True)  # Asegurarse de que el directorio exista
    with open(CSV_FILE, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "temperatura", "humedad"])

@app.post("/api/sensor-data")
async def recibir_datos(data: SensorData):
    # Establecer la zona horaria de Chile
    chile_timezone = pytz.timezone('Chile/Continental')
    timestamp = datetime.now(chile_timezone).isoformat()
    
    with open(CSV_FILE, mode="a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, data.temperatura, data.humedad])
    print(f"[{timestamp}] Temp: {data.temperatura} °C | Hum: {data.humedad} %")
    return {"status": "ok", "timestamp": timestamp}
