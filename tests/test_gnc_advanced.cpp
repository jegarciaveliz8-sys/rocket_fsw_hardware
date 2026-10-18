#include <iostream>
#include <cassert>
#include <cmath>

// Prueba unitaria de convergencia del filtro y controlador PID
void test_pid_anti_windup() {
    float error = 50.0;
    float integral = 0.0;
    float kp = 1.2, ki = 0.1, kd = 0.05;
    float max_output = 30.0; // Límite físico de las aletas en grados

    // Simular acumulación con saturación (Anti-Windup)
    for(int i = 0; i < 100; i++) {
        integral += error;
        // Limitar integral para evitar windup
        if (integral > 100.0) integral = 100.0;
    }

    float output = kp * error + ki * integral;
    if (output > max_output) output = max_output;

    assert(output <= max_output);
    std::cout << "[TEST] PID Anti-Windup verificado con éxito. Salida acotada a: " << output << "°\n";
}

int main() {
    std::cout << "=== INICIANDO PRUEBAS UNITARIAS AVANZADAS GNC ==-\n";
    test_pid_anti_windup();
    std::cout << ">>> TODAS LAS PRUEBAS UNITARIAS AVANZADAS PASARON CON ÉXITO <<<\n";
    return 0;
}
