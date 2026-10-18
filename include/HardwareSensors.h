#ifndef HARDWARE_SENSORS_H
#define HARDWARE_SENSORS_H

#ifdef ARDUINO
#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>

class RealSensors {
private:
    Adafruit_MPU6050 mpu;
    bool imu_initialized = false;

public:
    bool begin() {
        Wire.begin();
        if (!mpu.begin()) {
            return false;
        }
        mpu.setAccelerometerRange(MPU6050_RANGE_16_G);
        mpu.setGyroRange(MPU6050_RANGE_500_DEG);
        mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
        imu_initialized = true;
        return true;
    }

    void readIMU(float &gx, float &gy, float &gz, float &ax, float &ay, float &az) {
        if (!imu_initialized) return;
        sensors_event_t a, g, temp;
        mpu.getEvent(&a, &g, &temp);

        // Convertir lecturas del sensor a unidades estándar del EKF
        ax = a.acceleration.x;
        ay = a.acceleration.y;
        az = a.acceleration.z;
        gx = g.gyro.x;
        gy = g.gyro.y;
        gz = g.gyro.z;
    }

    void readGPS(float &lat, float &lon, float &alt, bool &new_data) {
        // Lógica de lectura de trama NMEA (ej. TinyGPS++) por Serial1 del GPS físico
        new_data = false;
        if (Serial1.available()) {
            // Parser NMEA simplificado o integración de librería externa GPS
            new_data = true;
        }
    }
};

#endif
#endif
