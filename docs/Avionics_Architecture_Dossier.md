# Dossier de Arquitectura de Aviónica y Software de Vuelo (FSW)
**Proyecto:** Computadora de Vuelo y Sistema GNC para Cohetería de Alta Potencia  
**Versión:** 2.0 (GNC & EKF Integrated)  

---

## 1. Resumen Ejecutivo
El sistema representa una computadora de vuelo redundante y autónoma diseñada para la adquisición de telemetría de alta velocidad, estimación de estado no lineal mediante Filtro de Kalman Extendido (EKF), control activo de superficies aerodinámicas (PID con Anti-Windup) y gestión segura de pirotecnia de recuperación.

## 2. Arquitectura de Navegación, Guiado y Control (GNC)
* **Navegación (EKF):**
  - Matriz de estado: $x = [p_z, v_z, a_z]^T$ (Posición, Velocidad y Aceleración en eje Z).
  - Tasa de ejecución: 100 Hz / 400 Hz.
  - Corrección: Barómetro BMP280 con matriz de covarianza de medición $R = 2.5$.
* **Control Activo (PID):**
  - Control de actitud de cabeceo/guiño mediante actuación de aletas (*canards*).
  - Algoritmo de integración con Anti-Windup para evitar saturación de actuadores.

## 3. Seguridad Crítica y Tolerancia a Fallos
- **Watchdog Timer (WDT):** Reinicio automático por bloqueo de ejecución en < 100 ms.
- **Doble criterio de comprobación de apogeo:** Validación por velocidad residual ($v_z \le 0$) y caída acumulada de altitud ($p_{max} - p_z > 1.0\,\text{m}$).
- **Aislamiento Galvánico:** Despliegue pirotécnico mediante MOSFET N-Channel (IRLZ44N) desacoplado por optoacoplador.
