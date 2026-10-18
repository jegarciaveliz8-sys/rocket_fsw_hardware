#include "flight_state.h"
#include "config.h"
#include <Arduino.h>

static FlightState current_state = IDLE;
static float max_altitude = 0.0;

void updateFlightState(float az, float current_altitude) {
    switch (current_state) {
        case IDLE:
            if (az > LAUNCH_ACCEL_THRESHOLD) {
                current_state = BOOST;
            }
            break;
            
        case BOOST:
            if (az < 1.0) { // Fin de empuje del motor
                current_state = COAST;
                max_altitude = current_altitude;
            }
            break;
            
        case COAST:
            if (current_altitude > max_altitude) {
                max_altitude = current_altitude;
            }
            
            // Doble criterio de apogeo: Inversión de aceleración vertical o caída de altitud
            if (current_altitude < (max_altitude - APOGEE_ALTITUDE_DROP)) {
                current_state = APOGEE;
                digitalWrite(PYRO_PIN, HIGH); // Disparo físico de la pirotecnia
            }
            break;
            
        case APOGEE:
            current_state = RECOVERY;
            break;
            
        case RECOVERY:
            break;
    }
}

FlightState getCurrentFlightState() {
    return current_state;
}
