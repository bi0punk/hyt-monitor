#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <Adafruit_SHT31.h>
#include <ArduinoJson.h>

// Reemplaza con tus datos WiFi
const char* ssid = "CAPI";
const char* password = "NOAH2016";

const char* serverURL = "http://192.168.1.136:8000/api/sensor-data";  // IP de tu servidor FastAPI

Adafruit_SHT31 sht31 = Adafruit_SHT31();

void setup() {
  Serial.begin(115200);
  Wire.begin(21, 22);  // Ajusta SDA/SCL si usas otros

  WiFi.begin(ssid, password);
  Serial.print("Conectando a WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nConectado a WiFi");

  if (!sht31.begin(0x44)) {
    Serial.println("No se encontró el sensor SHT3x.");
    while (1) delay(1);
  }
}

void loop() {
  float temp = sht31.readTemperature();
  float hum = sht31.readHumidity();

  if (!isnan(temp) && !isnan(hum)) {
    StaticJsonDocument<200> jsonDoc;
    jsonDoc["temperatura"] = temp;
    jsonDoc["humedad"] = hum;

    String jsonStr;
    serializeJson(jsonDoc, jsonStr);

    HTTPClient http;
    http.begin(serverURL);
    http.addHeader("Content-Type", "application/json");

    int httpResponseCode = http.POST(jsonStr);
    Serial.print("Código respuesta: ");
    Serial.println(httpResponseCode);

    http.end();
  } else {
    Serial.println("Error leyendo sensor.");
  }

  delay(3000);  // Cada 5 segundos
}
