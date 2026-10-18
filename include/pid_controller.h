#pragma once

class PIDController {
private:
    float kp, ki, kd;
    float integral;
    float previous_error;
    float output_min, output_max;

public:
    PIDController(float p, float i, float d, float min_val, float max_val) {
        kp = p;
        ki = i;
        kd = d;
        integral = 0.0f;
        previous_error = 0.0f;
        output_min = min_val;
        output_max = max_val;
    }

    float compute(float setpoint, float measured, float dt) {
        float error = setpoint - measured;

        // Término Proporcional
        float p_out = kp * error;

        // Término Integral con Anti-Windup (evita acumulación excesiva)
        integral += error * dt;
        if (integral > output_max) integral = output_max;
        else if (integral < output_min) integral = output_min;
        float i_out = ki * integral;

        // Término Derivativo (sobre la tasa de cambio del error)
        float derivative = (error - previous_error) / dt;
        float d_out = kd * derivative;

        // Salida total de control (ej. grados de deflexión de los servomotores)
        float output = p_out + i_out + d_out;

        // Saturación de los actuadores físicos
        if (output > output_max) output = output_max;
        else if (output < output_min) output = output_min;

        previous_error = error;
        return output;
    }
};
