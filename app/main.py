import csv
import logging
import os
import threading
import time
from datetime import datetime, timedelta

import pytz
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

app = FastAPI()

API_KEY = os.environ.get("HYT_API_KEY", "")

CSV_FILE = os.environ.get("HYT_CSV_FILE", "/app/sensor_data/datos_sensor.csv")
_csv_lock = threading.Lock()

if not os.path.exists(CSV_FILE):
    os.makedirs(os.path.dirname(CSV_FILE), exist_ok=True)
    with open(CSV_FILE, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "temperatura", "humedad"])


class SensorData(BaseModel):
    temperatura: float = Field(..., ge=-50, le=100)
    humedad: float = Field(..., ge=0, le=100)


def rotate_csv_if_needed():
    MAX_SIZE = 10 * 1024 * 1024
    if os.path.exists(CSV_FILE) and os.path.getsize(CSV_FILE) > MAX_SIZE:
        ts = time.strftime("%Y%m%d_%H%M%S")
        rotated = f"{CSV_FILE}.{ts}"
        os.rename(CSV_FILE, rotated)
        with open(CSV_FILE, mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "temperatura", "humedad"])
        log.info("CSV rotated: %s", rotated)


def require_auth(request: Request):
    if API_KEY:
        auth = request.headers.get("X-API-Key", "")
        if auth != API_KEY:
            raise HTTPException(status_code=401, detail="API Key inválida")


_rate_limit_store: dict[str, list[float]] = {}
_rate_limit_max = int(os.environ.get("HYT_RATE_LIMIT", "60"))
_rate_window = 60


def check_rate_limit(request: Request):
    ip = request.client.host if request.client else "unknown"
    now = time.time()
    window_start = now - _rate_window
    timestamps = _rate_limit_store.get(ip, [])
    timestamps = [t for t in timestamps if t > window_start]
    if len(timestamps) >= _rate_limit_max:
        raise HTTPException(status_code=429, detail="Demasiadas peticiones")
    timestamps.append(now)
    _rate_limit_store[ip] = timestamps


@app.post("/api/sensor-data")
async def recibir_datos(data: SensorData, request: Request):
    require_auth(request)
    check_rate_limit(request)

    chile_timezone = pytz.timezone("Chile/Continental")
    timestamp = datetime.now(chile_timezone).isoformat()

    with _csv_lock:
        rotate_csv_if_needed()
        with open(CSV_FILE, mode="a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, data.temperatura, data.humedad])

    log.info("[%s] Temp: %.2f °C | Hum: %.2f %%", timestamp, data.temperatura, data.humedad)
    return {"status": "ok", "timestamp": timestamp}


@app.get("/api/sensor-data")
async def obtener_datos(request: Request, limit: int = 100):
    require_auth(request)
    check_rate_limit(request)

    rows = []
    with _csv_lock:
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, mode="r", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    rows.append(row)

    return {"data": rows[-limit:] if limit > 0 else rows, "count": len(rows)}
