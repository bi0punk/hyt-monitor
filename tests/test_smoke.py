"""Smoke tests para hyt-monitor: POST /api/sensor-data escribe CSV."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    csv_file = tmp_path / "datos_sensor.csv"
    monkeypatch.setenv("HYT_CSV_FILE", str(csv_file))
    # Forzar reimport para que app.main lea el nuevo path en la inicialización.
    import importlib

    import app.main as mainmod
    importlib.reload(mainmod)
    from fastapi.testclient import TestClient

    with TestClient(mainmod.app) as c:
        yield c, csv_file


def test_post_sensor_data_writes_csv(client):
    c, csv_file = client
    r = c.post("/api/sensor-data", json={"temperatura": 22.5, "humedad": 60.0})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["status"] == "ok"
    assert "timestamp" in body

    # El CSV debe tener cabecera + 1 fila
    content = csv_file.read_text()
    lines = content.strip().splitlines()
    assert lines[0] == "timestamp,temperatura,humedad"
    assert len(lines) == 2
    assert "22.5" in lines[1] and "60.0" in lines[1]


def test_post_validates_ranges(client):
    c, _ = client
    # temperatura fuera de rango (-50..100)
    r = c.post("/api/sensor-data", json={"temperatura": -999, "humedad": 60.0})
    assert r.status_code == 422
    # humedad fuera de rango (0..100)
    r = c.post("/api/sensor-data", json={"temperatura": 20.0, "humedad": 150.0})
    assert r.status_code == 422
