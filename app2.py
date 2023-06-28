from fastapi import FastAPI
from pydantic import BaseModel
from termcolor import colored

app = FastAPI()

class SensorData(BaseModel):
    temperature: float

@app.post("/sensor")
async def receive_sensor_data(sensor_data: SensorData):
    temperature = sensor_data.temperature
    temperature_text = colored("temperature", attrs=["bold"])
    colored_temperature = colored(temperature, "green", attrs=["bold"])
    print(f"{temperature_text}: {colored_temperature}")
    return {"message": "Datos recibidos correctamente"}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="192.168.1.129", port=8000)