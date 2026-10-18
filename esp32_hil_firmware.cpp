#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>

const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* server_url = "http://YOUR_SERVER_IP:8000/api/hil/ingest"\;

Adafruit_MPU6050 mpu;

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi Connected to ODYSSEY-1 Network");

  if (!mpu.begin()) {
    Serial.println("Error localizando sensor MPU6050!");
    while (1) { delay(10); }
  }
  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
}

void loop() {
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(server_url);
    http.addHeader("Content-Type", "application/json");

    String jsonPayload = "{\"payload_json\": \"{\\\"ax\\\": " + String(a.acceleration.x, 4) + 
                         ", \\\"ay\\\": " + String(a.acceleration.y, 4) + 
                         ", \\\"az\\\": " + String(a.acceleration.z, 4) + "}\"}";

    int httpResponseCode = http.POST(jsonPayload);
    if (httpResponseCode > 0) {
      Serial.printf("HIL Packet Sent. Code: %d\n", httpResponseCode);
    }
    http.end();
  }
  delay(100); // 10 Hz HIL Ingestion Rate
}
