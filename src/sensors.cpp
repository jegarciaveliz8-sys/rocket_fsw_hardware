#include <Adafruit_MPU6050.h>
#include <Adafruit_BMP280.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include "sensors.h"

Adafruit_MPU6050 mpu;
Adafruit_BMP280 bmp; // I2C

bool initSensors() {
    Wire.begin();
    
    if (!mpu.begin()) {
        return false;
    }
    mpu.setAccelerometerRange(MPU6050_RANGE_16_G);
    mpu.setGyroRange(MPU6050_RANGE_500_DEG);
    mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);

    if (!bmp.begin(0x76)) { // Dirección I2C típica del BMP280 (puede ser 0x77)
        return false;
    }
    
    // Configuración recomendada para altimetría
    bmp.setSampling(Adafruit_BMP280::MODE_NORMAL,     /* Operating Mode. */
                    Adafruit_BMP280::SAMPLING_X2,     /* Temp. oversampling */
                    Adafruit_BMP280::SAMPLING_X16,    /* Pressure oversampling */
                    Adafruit_BMP280::FILTER_X16,      /* Filtering. */
                    Adafruit_BMP280::STANDBY_MS_500); /* Standby time. */

    return true;
}

void readSensors(float &ax, float &ay, float &az, float &altitude) {
    sensors_event_t a, g, temp;
    mpu.getEvent(&a, &g, &temp);
    ax = a.acceleration.x;
    ay = a.acceleration.y;
    az = a.acceleration.z;

    altitude = bmp.readAltitude(1013.25); // Altitud aproximada basada en presión estándar a nivel del mar
}
