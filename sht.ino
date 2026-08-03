#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <Adafruit_SHT31.h>
#include <ArduinoJson.h>
#include "credentials.h"

Adafruit_SHT31 sht31 = Adafruit_SHT31();

void setup() {
  Serial.begin(115200);
  Wire.begin(21, 22);  // Ajusta SDA/SCL si usas otros

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
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
    http.begin(SERVER_URL);
    http.addHeader("Content-Type", "application/json");

    int httpResponseCode = http.POST(jsonStr);
    if (httpResponseCode > 0) {
      Serial.print("Código respuesta: ");
      Serial.println(httpResponseCode);
    } else {
      Serial.print("Error HTTP: ");
      Serial.println(httpResponseCode);
    }
    http.end();
  } else {
    Serial.println("Error leyendo sensor.");
  }

  delay(5000);
}
