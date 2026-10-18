#include <Arduino.h>
#include "telemetry.h"

void sendTelemetry(unsigned long timestamp, int state, float ax, float ay, float az, float altitude) {
    // Formato CSV por Serial: Timestamp, Estado, Ax, Ay, Az, Altitud
    Serial.print(timestamp);
    Serial.print(",");
    Serial.print(state);
    Serial.print(",");
    Serial.print(ax, 2);
    Serial.print(",");
    Serial.print(ay, 2);
    Serial.print(",");
    Serial.print(az, 2);
    Serial.print(",");
    Serial.println(altitude, 2);
}

uint8_t calculateCRC(const uint8_t *data, size_t length) {
    uint8_t crc = 0;
    for (size_t i = 0; i < length; i++) {
        crc ^= data[i];
    }
    return crc;
}
