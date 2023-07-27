from fastapi import FastAPI, Request
from pydantic import BaseModel
from termcolor import colored
from fastapi.templating import Jinja2Templates
import json
from fastapi.responses import JSONResponse
from datetime import datetime

app = FastAPI()
templates = Jinja2Templates(directory="templates")

class SensorData(BaseModel):
    temperature: float

data_file = "data.json"
data = []

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/sensor")
async def receive_sensor_data(sensor_data: SensorData):
    temperature = sensor_data.temperature
    temperature_text = colored("temperature", "blue", attrs=["bold"])
    colored_temperature = colored(temperature, "green", attrs=["bold"])
    message = f"{temperature_text}: {colored_temperature}"
    print(f"{temperature_text}: {colored_temperature}")

    sensor_id = len(data) + 1
    current_datetime = datetime.now()

    data_entry = {
        "id": sensor_id,
        "temperatura": temperature,
        "fecha": current_datetime.strftime("%Y-%m-%d"),
        "hora": current_datetime.strftime("%H:%M:%S")
    }

    data.append(data_entry)
    with open(data_file, "a") as file:
        json.dump(data_entry, file, indent=2)
        file.write("\n")  

    return {"message": "Datos recibidos correctamente"}


@app.get("/data")
async def get_data():
    return data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="192.168.1.129", port=8000)
