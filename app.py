from fastapi import FastAPI, Request
from pydantic import BaseModel
from termcolor import colored
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
import json
import sqlite3
import datetime
import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory="templates")

data_file = "data.json"
database = 'sensor_data.db'

class SensorData(BaseModel):
    temperature: float

def get_db_connection():
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    return conn

def save_sensor_data(temperature):
    conn = get_db_connection()
    current_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sensor_data (temperature, timestamp) VALUES (?, ?)", (temperature, current_datetime))
    conn.commit()
    conn.close()

def fetch_sensor_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, temperature, timestamp FROM sensor_data")
    sensor_data = [{'id': row['id'], 'temperature': row['temperature'], 'timestamp': row['timestamp']} for row in cursor.fetchall()]
    conn.close()
    return sensor_data

def obtener_temperatura_minima():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, temperature FROM sensor_data WHERE temperature = (SELECT MIN(temperature) FROM sensor_data)")
    temperatura_minima = cursor.fetchone()[0]
    conn.close()
    return temperatura_minima

@app.get("/")
async def home(request: Request):
    ultimo = fetch_sensor_data()[-1]
    temperature = ultimo.get('temperature')
    date_event = ultimo.get('timestamp')
    minima_temp = obtener_temperatura_minima()
    return templates.TemplateResponse("index.html", {"request": request, "temperature": temperature, "date_event": date_event, "minima_temp": minima_temp})

@app.post("/sensor")
async def receive_sensor_data(sensor_data: SensorData):
    temperature = sensor_data.temperature

    # Print formatted sensor data
    temperature_text = colored("temperature", "blue", attrs=["bold"])
    colored_temperature = colored(temperature, "green", attrs=["bold"])
    message = f"{temperature_text}: {colored_temperature}"
    print(f"{temperature_text}: {colored_temperature}")

    # Save data to the database
    save_sensor_data(temperature)

    # Append data to JSON file
    sensor_id = len(fetch_sensor_data()) + 1
    current_datetime = datetime.now()
    data_entry = {
        "id": sensor_id,
        "temperatura": temperature,
        "fecha": current_datetime.strftime("%Y-%m-%d"),
        "hora": current_datetime.strftime("%H:%M:%S")
    }

    with open(data_file, "a") as file:
        json.dump(data_entry, file, indent=2)
        file.write("\n")  

    return {"message": "Datos recibidos correctamente"}

@app.get("/data")
def get_data():
    ultimo = fetch_sensor_data()[-1]
    temperature = ultimo.get('temperature')
    return JSONResponse(content={"temperature": temperature})

if __name__ == "__main__":
    uvicorn.run(app)
