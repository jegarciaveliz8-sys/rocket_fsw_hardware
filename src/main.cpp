#include <Arduino.h>
#include "config.h"
#include "sensors.h"
#include "flight_state.h"
#include "logger.h"
#include "kalman_filter.h"
#include "pid_controller.h"

// Instancias de estimación de estado y control
ExtendedKalmanFilter ekf(0.01f, 2.5f);
PIDController pid_canards(1.2f, 0.05f, 0.1f, -30.0f, 30.0f);

unsigned long last_update_time = 0;

void setup() {
    Serial.begin(115200);
    initSensors();
    initLogger();
    initFlightState();
    last_update_time = micros();
}

void loop() {
    unsigned long current_time = micros();
    float dt = (current_time - last_update_time) / 1000000.0f;
    if (dt <= 0.0f) dt = 0.01f;
    last_update_time = current_time;

    // 1. Lectura de sensores físicos
    SensorData raw_data = readSensors();

    // 2. Ejecutar Filtro de Kalman Extendido (EKF)
    ekf.predict(dt, raw_data.az);
    ekf.update(raw_data.altitude);

    float filtered_alt = ekf.getPosition();
    float filtered_vel = ekf.getVelocity();

    // 3. Ejecutar Lazo de Control Activo PID (si está en estado de ascenso/BOOST/COAST)
    float fin_angle = pid_canards.compute(0.0f, raw_data.gyro_x, dt);

    // 4. Actualizar máquina de estados utilizando la altitud y velocidad filtradas por EKF
    updateFlightState(raw_data.az, filtered_alt, filtered_vel);

    // 5. Telemetría y registro local en tarjeta SD
    logData(raw_data, filtered_alt, filtered_vel);
    
    // Transmisión de telemetría por puerto serie / radio
    Serial.printf("%lu,%d,%.2f,%.2f,%.2f,%.2f\n", 
                  millis(), getFlightState(), raw_data.ax, raw_data.ay, raw_data.az, filtered_alt);

    delay(10); // Lazo de ejecución a 100 Hz
}
