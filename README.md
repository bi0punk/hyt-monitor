# hyt-monitor

[![CI](https://github.com/bi0punk/hyt-monitor/actions/workflows/ci.yml/badge.svg)](https://github.com/bi0punk/hyt-monitor/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Temperature and humidity monitoring system. An ESP32 with an SHT31 sensor reads environmental data and sends it to a FastAPI server via HTTP POST. The server stores data in a rotating CSV and exposes a REST endpoint.

## Tabla de contenidos

- [Características](#características)
- [Stack](#stack)
- [Arquitectura](#arquitectura)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Uso](#uso)
- [Tests](#tests)
- [CI](#ci)
- [Configuración](#configuración)
- [Datos](#datos)
- [Limitaciones y roadmap](#limitaciones-y-roadmap)
- [Licencia](#licencia)

## Características

- Firmware ESP32 (SHT31) que POSTea lecturas a un servidor FastAPI.
- Validación de rangos con Pydantic (temperatura -50..100 °C, humedad 0..100 %).
- Persistencia en CSV con rotación automática a los 10 MB.
- Timestamp en zona horaria `Chile/Continental`.
- Despliegue con Docker + volumen persistente para `sensor_data/`.

## Stack

- **Lenguaje**: Python 3.12+ (servidor) · C++/Arduino (firmware ESP32).
- **Web**: FastAPI + Uvicorn.
- **Sensor**: SHT31 (I2C) vía firmware `sht.ino`.
- **Persistencia**: CSV rotante.
- **TZ**: pytz (`Chile/Continental`).
- **Calidad**: ruff (lint), pytest.
- **Despliegue**: Docker (`python:3.11`) + Docker Compose.

## Arquitectura

```
ESP32 + SHT31  ──HTTP POST──►  FastAPI (app.main)  ──append──►  sensor_data/datos_sensor.csv
                                              (rotación 10MB)
```

- El ESP32 lee temperatura/humedad del SHT31 y hace `POST /api/sensor-data`.
- El servidor valida con Pydantic, timestampa y appenda al CSV (rotación a 10MB).
- `sensor_data/` se monta como volumen en Docker para persistencia.

## Requisitos

- Python 3.12+ (o Docker).
- ESP32 + sensor SHT31 para el firmware (opcional para solo servidor).
- Wi-Fi entre ESP32 y el host del servidor.

## Instalación

Con Docker (recomendado):

```bash
docker compose up -d --build
```

Sin Docker:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Uso

### ESP32

Flashea `sht.ino` al ESP32 con Arduino IDE (ajusta SSID, password y URL del servidor en el sketch).

### Servidor

La API queda en `http://localhost:8000`.

Endpoint:

```bash
curl -X POST http://localhost:8000/api/sensor-data \
  -H 'Content-Type: application/json' \
  -d '{"temperatura": 22.5, "humedad": 60.0}'
```

Respuesta:

```json
{"status": "ok", "timestamp": "2026-07-02T...-04:00"}
```

## Tests

```bash
pytest -q
```

Cobertura (`tests/test_smoke.py`): POST de lectura válida (verifica escritura de CSV cabecera+fila) y validación de rangos (422 para valores fuera de rango). Usa `HYT_CSV_FILE` para apuntar a un CSV efímero.

## CI

GitHub Actions (`.github/workflows/ci.yml`) sobre Python 3.12:

- **lint** — `ruff check .`
- **test** — instala deps + `pytest -q`

## Configuración

Variables de entorno:

- `HYT_CSV_FILE` — ruta del CSV (default `/app/sensor_data/datos_sensor.csv`, útil para tests).
- En el firmware (`sht.ino`): SSID, password y URL del servidor.

## Datos

- `sensor_data/datos_sensor.csv` — datos persistidos (cabecera: `timestamp,temperatura,humedad`). Rotación a los 10 MB con sufijo timestamp. Gitignored (se regenera al arrancar).

## Limitaciones y roadmap

- **Limitación**: sin endpoint de lectura/consulta (solo ingestión). Para analizar datos, leer el CSV directo.
- **Limitación**: sin autenticación ni HTTPS; usar tras VPN/reverse proxy si se expone.
- **Roadmap**: endpoint GET de histórico, persistencia en SQLite opcional, dashboard básico.

## Licencia

MIT — ver [LICENSE](LICENSE).
