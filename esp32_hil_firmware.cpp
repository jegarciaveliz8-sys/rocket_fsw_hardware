/**
 * @file esp32_hil_firmware.cpp
 * @brief Firmware HIL de Tiempo Real con FreeRTOS y Filtro de Fusión Sensorial Mahony AHRS
 * @target ESP32-WROOM-32 / STM32F4 Dual-Core RTOS
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>

// Parámetros de red de grado industrial MCC
const char* WIFI_SSID = "ODYSSEY_MCC_SECURE_NET";
const char* WIFI_PASS = "AES256_MISSION_DIRECTOR_KEY";
const char* MCC_HIL_ENDPOINT = "http://192.168.1.100:8000/api/hil/ingest"\;

Adafruit_MPU6050 mpu;

// Variables Globales Sincronizadas por Mutex RTOS
SemaphoreHandle_t xSensorMutex;
struct CalibratedIMUPacket {
    float ax, ay, az;
    float gx, gy, gz;
    uint32_t timestamp_us;
} g_imu_data;

// Parámetros del Filtro Mahony AHRS
float q0 = 1.0f, q1 = 0.0f, q2 = 0.0f, q3 = 0.0f;
float twoKp = 2.0f * 0.5f; // Ganancia proporcional
float twoKi = 2.0f * 0.0f; // Ganancia integral

// Algoritmo de Fusión Sensorial Mahony (6-DOF Quaternion AHRS)
void mahonyAHRSupdateIMU(float gx, float gy, float gz, float ax, float ay, float az, float dt) {
    float recipNorm;
    float halfvx, halfvy, halfvz;
    float halfex, halfey, halfez;
    float qa, qb, qc;

    if(!((ax == 0.0f) && (ay == 0.0f) && (az == 0.0f))) {
        recipNorm = 1.0f / sqrtf(ax * ax + ay * ay + az * az);
        ax *= recipNorm; ay *= recipNorm; az *= recipNorm;

        halfvx = q1 * q3 - q0 * q2;
        halfvy = q0 * q1 + q2 * q3;
        halfvz = q0 * q0 - 0.5f + q3 * q3;

        halfex = (ay * halfvz - az * halfvy);
        halfey = (az * halfvx - ax * halfvz);
        halfez = (ax * halfvy - ay * halfvx);

        gx += twoKp * halfex; gy += twoKp * halfey; gz += twoKp * halfez;
    }

    gx *= (0.5f * dt); gy *= (0.5f * dt); gz *= (0.5f * dt);
    qa = q0; qb = q1; qc = q2;
    q0 += (-qb * gx - qc * gy - q3 * gz);
    q1 += (qa * gx + qc * gz - q3 * gy);
    q2 += (qa * gy - qb * gz + q3 * gx);
    q3 += (qa * gz + qb * gy - qc * gx);

    recipNorm = 1.0f / sqrtf(q0 * q0 + q1 * q1 + q2 * q2 + q3 * q3);
    q0 *= recipNorm; q1 *= recipNorm; q2 *= recipNorm; q3 *= recipNorm;
}

// TAREA RTOS CORE 0: Muestreo IMU de alta velocidad (100 Hz)
void TaskSensorRead(void *pvParameters) {
    TickType_t xLastWakeTime = xTaskGetTickCount();
    const TickType_t xFrequency = pdMS_TO_TICKS(10); // 10ms = 100 Hz

    for (;;) {
        sensors_event_t a, g, temp;
        mpu.getEvent(&a, &g, &temp);

        xSemaphoreTake(xSensorMutex, portMAX_DELAY);
        g_imu_data.ax = a.acceleration.x;
        g_imu_data.ay = a.acceleration.y;
        g_imu_data.az = a.acceleration.z;
        g_imu_data.gx = g.gyro.x;
        g_imu_data.gy = g.gyro.y;
        g_imu_data.gz = g.gyro.z;
        g_imu_data.timestamp_us = micros();
        
        mahonyAHRSupdateIMU(g.gyro.x, g.gyro.y, g.gyro.z, a.acceleration.x, a.acceleration.y, a.acceleration.z, 0.01f);
        xSemaphoreGive(xSensorMutex);

        vTaskDelayUntil(&xLastWakeTime, xFrequency);
    }
}

// TAREA RTOS CORE 1: Transmisión Teleimétrica HTTP/JSON a MCC (20 Hz)
void TaskTelemetryUplink(void *pvParameters) {
    HTTPClient http;

    for (;;) {
        if (WiFi.status() == WL_CONNECTED) {
            CalibratedIMUPacket local_packet;
            xSemaphoreTake(xSensorMutex, portMAX_DELAY);
            local_packet = g_imu_data;
            xSemaphoreGive(xSensorMutex);

            http.begin(MCC_HIL_ENDPOINT);
            http.addHeader("Content-Type", "application/json");

            char payload[256];
            snprintf(payload, sizeof(payload),
                     "{\"payload_json\":\"{\\\"ax\\\":%.4f,\\\"ay\\\":%.4f,\\\"az\\\":%.4f,\\\"q0\\\":%.4f,\\\"q1\\\":%.4f,\\\"q2\\\":%.4f,\\\"q3\\\":%.4f}\"}",
                     local_packet.ax, local_packet.ay, local_packet.az, q0, q1, q2, q3);

            int httpCode = http.POST(payload);
            http.end();
        }
        vTaskDelay(pdMS_TO_TICKS(50)); // 20 Hz
    }
}

void setup() {
    Serial.begin(115200);
    xSensorMutex = xSemaphoreCreateMutex();

    Wire.begin();
    if (!mpu.begin()) {
        Serial.println("CRITICAL FAULT: MPU6050 Hardware Not Detected!");
        while (1);
    }

    WiFi.begin(WIFI_SSID, WIFI_PASS);

    // Asignación de Tareas Multithreading a Cores independientes
    xTaskCreatePinnedToCore(TaskSensorRead, "SensorReadTask", 4096, NULL, 2, NULL, 0);
    xTaskCreatePinnedToCore(TaskTelemetryUplink, "TelemetryTask", 8192, NULL, 1, NULL, 1);
}

void loop() {
    vTaskDelete(NULL); // Libera el hilo principal en RTOS
}
