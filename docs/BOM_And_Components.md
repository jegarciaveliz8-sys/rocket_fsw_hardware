# Lista de Materiales y Componentes (BOM) - Aviónica FSW v2.0

## 1. Sistema de Procesamiento y Sensores
* **Teensy 4.1:** Microcontrolador principal (ARM Cortex-M7 @ 600 MHz).
* **MPU6050:** IMU de 6 ejes (Acelerómetro / Giroscopio, bus I2C).
* **BMP280:** Sensor barométrico de alta precisión (Altitud y Presión, bus I2C).

## 2. Circuito de Potencia y Pirotecnia
* **MOSFET N-Channel (IRLZ44N):** Conmutación lógica de alta corriente para ignición de cargas pirotécnicas.
* **Optoacoplador (PC817):** Aislamiento galvánico entre la lógica de control de la Teensy y el circuito de potencia.
* **Resistencias:** 
  * 1x $220\,\Omega$ (Limitación de corriente en diodo del optoacoplador).
  * 1x $10\,\text{k}\Omega$ (Resistencia Pull-down para la puerta del MOSFET).
* **Diodo de Protección (1N4007):** Supresión de picos de voltaje inductivo (Flyback diode) en paralelo con el encendedor pirotécnico.

## 3. Conectividad y Estructura
* **Módulo de Telemetría RF:** Módulo LoRa (ej. SX1276 / E22) o par de XBee para transmisión serial bidireccional.
* **Conectores:** Bornes de tornillo de 2 pines para alimentación LiPo (7.4V - 11.1V) y salida pirotécnica.
