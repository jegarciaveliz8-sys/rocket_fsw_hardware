#pragma once

void sendTelemetry(unsigned long timestamp, int state, float ax, float ay, float az, float altitude);
uint8_t calculateCRC(const uint8_t *data, size_t length);
