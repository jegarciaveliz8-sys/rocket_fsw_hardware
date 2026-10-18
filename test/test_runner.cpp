#include <iostream>
#include <cassert>

// Emulación de estados de vuelo para pruebas en PC
enum FlightState { IDLE = 0, BOOST = 1, COAST = 2, APOGEE = 3, RECOVERY = 4 };

FlightState current_state = IDLE;
float max_altitude = 0.0;
bool pyro_triggered = false;

void updateFlightStateTest(float az, float current_altitude) {
    switch (current_state) {
        case IDLE:
            if (az > 3.0) current_state = BOOST;
            break;
        case BOOST:
            if (az < 1.0) {
                current_state = COAST;
                max_altitude = current_altitude;
            }
            break;
        case COAST:
            if (current_altitude > max_altitude) max_altitude = current_altitude;
            if (current_altitude < (max_altitude - 1.0)) {
                current_state = APOGEE;
                pyro_triggered = true;
            }
            break;
        case APOGEE:
            current_state = RECOVERY;
            break;
        case RECOVERY:
            break;
    }
}

int main() {
    std::cout << "=== INICIANDO PRUEBAS UNITARIAS EN PC ===" << std::endl;

    // Test 1: Inicio en IDLE
    assert(current_state == IDLE);
    std::cout << "[PASS] Test 1: Estado inicial es IDLE" << std::endl;

    // Test 2: Transición a BOOST por aceleración
    updateFlightStateTest(4.5, 0.0);
    assert(current_state == BOOST);
    std::cout << "[PASS] Test 2: Transición correcta a BOOST (az > 3.0)" << std::endl;

    // Test 3: Transición a COAST al apagar motor
    updateFlightStateTest(0.5, 100.0);
    assert(current_state == COAST);
    std::cout << "[PASS] Test 3: Transición correcta a COAST" << std::endl;

    // Test 4: Ascenso continuo en COAST sin disparar pirotecnia
    updateFlightStateTest(0.1, 250.0);
    assert(current_state == COAST);
    assert(!pyro_triggered);
    std::cout << "[PASS] Test 4: Ascenso en COAST registrado correctamente" << std::endl;

    // Test 5: Transición a APOGEE y disparo de pirotecnia por caída de altitud
    updateFlightStateTest(-0.5, 248.5); // Descendió 1.5 m
    assert(current_state == APOGEE);
    assert(pyro_triggered);
    std::cout << "[PASS] Test 5: Detección de APOGEE y disparo de pirotecnia EXITOSOS!" << std::endl;

    std::cout << "\n>>> TODAS LAS PRUEBAS PASARON CON ÉXITO (100% LOGICA VALIDA) <<<" << std::endl;
    return 0;
}
