# hyt-monitor

Temperature and humidity monitoring system. An ESP32 with an SHT31 sensor reads environmental data and sends it to a FastAPI server via HTTP POST. The server stores data in SQLite and exposes REST endpoints.

## Stack

Python 3, FastAPI, Arduino/C++ (ESP32), SHT31 sensor, SQLite, Docker

## Components

- `sht.ino` — ESP32 firmware reading SHT31 sensor data
- `app.py` / `app/` — FastAPI server receiving sensor readings
- `docker-compose.yml` — Containerized deployment

## Usage

### ESP32
Flash `sht.ino` to the ESP32 board using Arduino IDE.

### Server
```bash
pip install -r requirements.txt
python app.py
```

Or with Docker:
```bash
docker compose up
```

## API

`POST /api/sensor-data` — Receive sensor readings (temperature, humidity)

## License

MIT
