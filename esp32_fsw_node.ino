#include <WiFi.h>
#include <WiFiUdp.h>

const char* ssid = "TU_WIFI_SSID";
const char* password = "TU_WIFI_PASSWORD";

IPAddress mccServerIP(192, 168, 1, 100); 
unsigned int mccPort = 5005;

WiFiUDP udp;
unsigned long counter = 0;

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  
  Serial.print("Conectando a Wi-Fi FSW...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n[OBC ESP32] Conectado a la red con IP: " + WiFi.localIP().toString());
  udp.begin(5005);
}

void loop() {
  counter++;

  float simulatedAlt = 410.5 + sin(counter * 0.2) * 5.0;
  float simulatedVel = 7670.0 + cos(counter * 0.2) * 2.0;
  float simulatedPitch = sin(counter * 0.1) * 15.0;
  float simulatedRoll = (counter * 2.0);

  String jsonPacket = "{";
  jsonPacket += "\"alt\":" + String(simulatedAlt, 2) + ",";
  jsonPacket += "\"vel\":" + String(simulatedVel, 2) + ",";
  jsonPacket += "\"pitch\":" + String(simulatedPitch, 2) + ",";
  jsonPacket += "\"roll\":" + String(simulatedRoll, 2) + ",";
  jsonPacket += "\"seq\":" + String(counter);
  jsonPacket += "}";

  udp.beginPacket(mccServerIP, mccPort);
  udp.write((const uint8_t*)jsonPacket.c_str(), jsonPacket.length());
  udp.endPacket();

  Serial.println("[HIL TX] Trama enviada al MCC: " + jsonPacket);
  delay(1000);
}
