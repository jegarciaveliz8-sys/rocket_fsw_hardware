#pragma once
#include <stdint.h>

// Empaquetado estricto sin relleno de memoria
#pragma pack(push, 1)
struct TelemetryPacket {
    uint8_t sync1 = 0xAA;         // Byte de sincronización 1
    uint8_t sync2 = 0x55;         // Byte de sincronización 2
    uint32_t timestamp_ms;        // Tiempo de misión en milisegundos
    uint8_t flight_state;         // Estado actual de la máquina de vuelo
    float ax, ay, az;             // Aceleraciones físicas (Gs)
    float filtered_alt;           // Altitud estimada por Filtro de Kalman (m)
    float velocity;               // Velocidad vertical estimada (m/s)
    uint16_t checksum;            // Código de redundancia cíclica (CRC-16)
};
#pragma pack(pop)
