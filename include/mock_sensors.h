#pragma once
#include <math.h>

class MockSensorSuite {
private:
    float current_time;
    float simulated_altitude;
    float simulated_acceleration;

public:
    MockSensorSuite() {
        current_time = 0.0;
        simulated_altitude = 0.0;
        simulated_acceleration = 0.0;
    }

    void update(float dt) {
        current_time += dt;
        // Simulación de fase de aceleración (0 a 2.5s) y caída libre / descenso
        if (current_time < 2.5) {
            simulated_acceleration = 5.8; // Gs
            simulated_altitude += 0.5 * 9.81 * simulated_acceleration * (dt * dt);
        } else if (current_time < 10.0) {
            simulated_acceleration = -1.0; // Descenso con paracaídas
            simulated_altitude -= 4.0 * dt;
            if (simulated_altitude < 0) simulated_altitude = 0.0;
        } else {
            simulated_acceleration = 0.0;
            simulated_altitude = 0.0;
        }
    }

    float read_barometer_altitude() {
        return simulated_altitude;
    }

    float read_imu_acceleration_z() {
        return simulated_acceleration;
    }
};
#pragma once
