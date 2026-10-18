#ifndef SENSOR_FUSION_H
#define SENSOR_FUSION_H

#include <cmath>
#include "MathQuat.h"

// Estructura de Estado Completa para el EKF
struct NavigationState {
    float x = 0.0f, y = 0.0f, z = 0.0f;       // Posición (m)
    float vx = 0.0f, vy = 0.0f, vz = 0.0f;   // Velocidad (m/s)
    Quaternion attitude;                     // Actitud (Cuaternión)
    float gyro_bias_x = 0.0f;                // Deriva del giroscopio
};

class ErrorStateEKF {
private:
    NavigationState state;

public:
    void init(float init_x, float init_y, float init_z) {
        state.x = init_x;
        state.y = init_y;
        state.z = init_z;
        state.attitude.w = 1.0f;
        state.attitude.x = 0.0f;
        state.attitude.y = 0.0f;
        state.attitude.z = 0.0f;
    }

    // Predicción de Alta Frecuencia (IMU a 1 kHz)
    void predict(float gx, float gy, float gz, float ax, float ay, float az, float dt) {
        // Compensar sesgo estimado del giroscopio
        float uncomp_gx = gx - state.gyro_bias_x;
        
        // Propagación de Actitud
        state.attitude.integrate(uncomp_gx, gy, gz, dt);

        // Propagación Cinemática simple (Aceleración a velocidad y posición)
        state.vx += ax * dt;
        state.vy += ay * dt;
        state.vz += (az - 9.81f) * dt; // Restando gravedad en Z

        state.x += state.vx * dt;
        state.y += state.vy * dt;
        state.z += state.vz * dt;
    }

    // Corrección de Baja Frecuencia (GPS / Posición Externa)
    void correctGPS(float gps_x, float gps_y, float gps_z) {
        // Ganancia de Kalman simplificada para corrección de deriva
        float alpha = 0.1f; 
        state.x += alpha * (gps_x - state.x);
        state.y += alpha * (gps_y - state.y);
        state.z += alpha * (gps_z - state.z);
    }

    NavigationState getState() const {
        return state;
    }
};

#endif
