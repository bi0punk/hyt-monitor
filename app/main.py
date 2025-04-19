from fastapi import FastAPI, Request
from pydantic import BaseModel

app = FastAPI()

class SensorData(BaseModel):
    temperatura: float
    humedad: float

@app.post("/api/sensor-data")
async def recibir_datos(data: SensorData):
    print(f"Temperatura: {data.temperatura} °C | Humedad: {data.humedad} %")
    return {"status": "ok"}
