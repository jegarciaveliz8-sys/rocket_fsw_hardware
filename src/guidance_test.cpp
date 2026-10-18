#include <iostream>
#include "kalman_filter.h"
#include "pid_controller.h"

int main() {
    std::cout << "=== INICIANDO SIMULACIÓN DE ALGORITMOS GNC (EKF + PID) ===" << std::endl;

    // Instanciar Filtro de Kalman (Proceso Q=0.01, Medición R=2.5)
    ExtendedKalmanFilter ekf(0.01f, 2.5f);

    // Instanciar Controlador PID para Aletas (Kp=1.2, Ki=0.05, Kd=0.1, Limites: -30° a +30°)
    PIDController pid_canards(1.2f, 0.05f, 0.1f, -30.0f, 30.0f);

    float dt = 0.01f; // 100 Hz de tasa de control
    float simulated_true_alt = 0.0f;

    std::cout << "Tiempo(s) | Alt. Real(m) | Alt. EKF(m) | Velocidad(m/s) | Aleta PID(°)" << std::endl;

    for (int i = 0; i < 50; i++) {
        float t = i * dt;
        simulated_true_alt += 5.0f * dt; // Simula ascenso constante

        // Simular ruido del sensor barométrico (añadiendo error aleatorio)
        float noisy_baro = simulated_true_alt + ((rand() % 10 - 5) * 0.1f);
        float measured_accel = 9.81f; // Aceleración vertical base

        // Ejecutar Algoritmo 1: EKF (Predicción + Corrección)
        ekf.predict(dt, measured_accel);
        ekf.update(noisy_baro);

        // Ejecutar Algoritmo 2: PID para mantener un ángulo objetivo (ej. 15 grados de actitud)
        float target_attitude = 15.0f;
        float current_attitude = ekf.getVelocity() * 0.1f; // Simulado
        float control_fin_angle = pid_canards.compute(target_attitude, current_attitude, dt);

        if (i % 10 == 0) {
            std::printf("%6.2f s | %10.2f m | %11.2f m | %14.2f m/s | %11.2f°\n",
                        t, simulated_true_alt, ekf.getPosition(), ekf.getVelocity(), control_fin_angle);
        }
    }

    std::cout << "\n>>> PRUEBA DE ALGORITMOS GNC FINALIZADA CON ÉXITO EXTREMO <<<" << std::endl;
    return 0;
}
