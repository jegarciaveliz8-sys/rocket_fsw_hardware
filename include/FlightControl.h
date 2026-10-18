#ifndef FLIGHT_CONTROL_H
#define FLIGHT_CONTROL_H

#include <algorithm>

struct PIDConfig {
    float kp = 1.2f;
    float ki = 0.05f;
    float kd = 0.1f;
    float i_max = 100.0f;
};

class PIDController {
private:
    PIDConfig cfg;
    float integral = 0.0f;
    float prev_error = 0.0f;

public:
    PIDController(PIDConfig config) : cfg(config) {}

    float update(float setpoint, float measured, float dt) {
        float error = setpoint - measured;
        integral += error * dt;
        integral = std::clamp(integral, -cfg.i_max, cfg.i_max);
        
        float derivative = (error - prev_error) / dt;
        prev_error = error;

        return (cfg.kp * error) + (cfg.ki * integral) + (cfg.kd * derivative);
    }

    void reset() {
        integral = 0.0f;
        prev_error = 0.0f;
    }
};

// Sistema FDIR (Fault Detection, Isolation, and Recovery)
enum NavigationMode {
    NAV_FULL_GPS_EKF = 0,
    NAV_DEAD_RECKONING = 1 // Modo inercial puro por fallo/jamming de GPS
};

class FDIRManager {
private:
    NavigationMode mode = NAV_FULL_GPS_EKF;
    unsigned long gps_timeout_counter = 0;

public:
    void notifyGpsUpdate() {
        gps_timeout_counter = 0;
        mode = NAV_FULL_GPS_EKF;
    }

    void update(unsigned long dt_ms) {
        gps_timeout_counter += dt_ms;
        // Si no hay señal GPS válida por más de 500 ms, cambiar a modo degradado
        if (gps_timeout_counter > 500) {
            mode = NAV_DEAD_RECKONING;
        }
    }

    NavigationMode getMode() const { return mode; }
    bool isDegraded() const { return mode == NAV_DEAD_RECKONING; }
};

#endif
