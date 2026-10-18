#include <Arduino.h>

// Definición de estados de la FSM
enum FlightState {
  PAD_IDLE,
  BOOST,
  COASTING,
  APOGEE_DETECTION,
  DROGUE_DESCENT,
  MAIN_DESCENT,
  LANDED
};

FlightState currentState = PAD_IDLE;

// Variables de estado del EKF simplificado
float est_altitude = 0.0;
float est_velocity = 0.0;
float dt = 0.01; // 100 Hz

void setup() {
  Serial.begin(115200);
  while (!Serial);
  Serial.println("[FSW HIL] Computadora de Vuelo Iniciada.");
}

void updateEKF(float accel_z, float baro_alt) {
  // Predicción cinemática
  est_velocity += accel_z * dt;
  est_altitude += est_velocity * dt;
  
  // Corrección simple de Kalman con barómetro
  float gain = 0.2;
  est_altitude += gain * (baro_alt - est_altitude);
}

void updateFSM(float accel_z) {
  switch (currentState) {
    case PAD_IDLE:
      if (accel_z > 2.0) {
        currentState = BOOST;
        Serial.println("[FSM] Transición a BOOST");
      }
      break;
    case BOOST:
      if (accel_z < 0.0) {
        currentState = COASTING;
        Serial.println("[FSM] Transición a COASTING");
      }
      break;
    case COASTING:
      if (est_velocity <= 0.5) {
        currentState = APOGEE_DETECTION;
        Serial.println("[FSM] ¡APOGEE DETECTADO! Activando Drogue.");
        currentState = DROGUE_DESCENT;
      }
      break;
    case DROGUE_DESCENT:
      if (est_altitude <= 100.0) {
        Serial.println("[FSM] Altitud < 100m. Desplegando Main.");
        currentState = MAIN_DESCENT;
      }
      break;
    case MAIN_DESCENT:
      if (est_altitude <= 2.0) {
        currentState = LANDED;
        Serial.println("[FSM] Aterrizaje confirmado.");
      }
      break;
    default:
      break;
  }
}

void loop() {
  // Simulación de lectura de sensores físicos (IMU y Barómetro)
  float simulated_accel = 1.0; 
  float simulated_baro = est_altitude + 5.0;

  updateEKF(simulated_accel, simulated_baro);
  updateFSM(simulated_accel);

  // Enviar telemetría por puerto Serial al sistema de tierra o módulo LoRa
  Serial.print("State:"); Serial.print(currentState);
  Serial.print(",Alt:"); Serial.print(est_altitude);
  Serial.print(",Vel:"); Serial.println(est_velocity);

  delay(10); // Lazo de 100 Hz
}
