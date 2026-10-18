#pragma once

class ExtendedKalmanFilter {
private:
    float x_est[3]; // Estado: [Posición (z), Velocidad (v), Aceleración (a)]
    float P[3][3];  // Matriz de covarianza de error
    float Q_process; // Ruido del proceso
    float R_measure; // Ruido de la medición (Barómetro)

public:
    ExtendedKalmanFilter(float q, float r) {
        x_est[0] = 0.0f;
        x_est[1] = 0.0f;
        x_est[2] = 0.0f;
        
        Q_process = q;
        R_measure = r;

        // Inicializar covarianza
        for(int i=0; i<3; i++) {
            for(int j=0; j<3; j++) {
                P[i][j] = (i == j) ? 1.0f : 0.0f;
            }
        }
    }

    // Paso de Predicción basado en la física del cohete (dt = intervalo de tiempo)
    void predict(float dt, float accel_input) {
        // Modelo cinemático no lineal: x = x + v*dt + 0.5*a*dt^2
        x_est[0] = x_est[0] + x_est[1] * dt + 0.5f * accel_input * dt * dt;
        x_est[1] = x_est[1] + accel_input * dt;
        x_est[2] = accel_input;

        // Actualización simplificada de la covarianza de error (Aproximación de Riccati)
        P[0][0] += Q_process + dt * (P[1][0] + P[0][1]) + dt * dt * P[1][1];
        P[1][1] += Q_process;
    }

    // Paso de Corrección / Actualización usando la medición directa del barómetro
    void update(float baro_altitude) {
        // Innovación (residuo entre medición y predicción)
        float y = baro_altitude - x_est[0];

        // Ganancia de Kalman simplificada para el estado de posición
        float S = P[0][0] + R_measure;
        float K[3];
        K[0] = P[0][0] / S;
        K[1] = P[1][0] / S;
        K[2] = P[2][0] / S;

        // Actualizar estimación de estado con la medición ponderada
        x_est[0] += K[0] * y;
        x_est[1] += K[1] * y;
        x_est[2] += K[2] * y;

        // Actualizar matriz de covarianza
        float p00_temp = P[0][0];
        float p10_temp = P[1][0];
        float p20_temp = P[2][0];

        P[0][0] -= K[0] * p00_temp;
        P[1][0] -= K[1] * p00_temp;
        P[2][0] -= K[2] * p00_temp;
    }

    float getPosition() { return x_est[0]; }
    float getVelocity() { return x_est[1]; }
    float getAcceleration() { return x_est[2]; }
};
#pragma once
