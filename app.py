from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
import datetime
import sqlite3
from termcolor import colored

app = FastAPI()
templates = Jinja2Templates(directory="templates")
database = 'sensor_data.db'


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


@app.get('/')
def index(request: Request):
    ultimo = fetch_sensor_data()[-1]
    temperature = ultimo.get('temperature')
    date_event = ultimo.get('timestamp')
    minima_temp = obtener_temperatura_minima()
    return templates.TemplateResponse('index.html', {"request": request, "temperature": temperature, "date_event": date_event, "minima_temp": minima_temp})


@app.get('/data')
def get_data():
    ultimo = fetch_sensor_data()[-1]
    temperature = ultimo.get('temperature')
    return JSONResponse(content={"temperature": temperature})


@app.post('/sensor')
async def receive_sensor_data(request: Request):
    data = await request.json()

    for key, value in data.items():
        formatted_key = colored(key, 'green', attrs=['bold'])  # Aplica color verde y estilo bold a la clave
        formatted_value = colored(value, 'blue', attrs=['bold'])  # Aplica color azul y estilo bold al valor
        formatted_data = f"{formatted_key}: {formatted_value}"
        print(formatted_data)

    if data is not None and 'temperature' in data:
        temperature = float(data['temperature'])
        save_sensor_data(temperature)
        rounded = round(temperature)
        return str(temperature)
    else:
        return 'error'


if __name__ == '__main__':
    uvicorn.run(app, host='192.168.1.104', port=8000, debug=True)
