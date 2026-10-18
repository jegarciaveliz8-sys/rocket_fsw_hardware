# Guía de Conexión de Hardware - Computadora de Vuelo FSW

## 1. Mapeo de Pines I2C (Sensores)
Conecta los pines SDA y SCL de los sensores MPU6050 y BMP280 en paralelo al bus principal I2C de la Teensy 4.1:
* Pin 18 (SDA0): Línea de datos I2C.
* Pin 19 (SCL0): Línea de reloj I2C.
* Alimentación: 3.3V y GND compartidos.

## 2. Interfaz de Disparo Pirotécnico
* Pin Digital 2 (Teensy) -> Anodo del optoacoplador PC817 (con resistencia de 220 ohm).
* Colector del optoacoplador -> Compuerta (Gate) del MOSFET IRLZ44N.
* Resistencia de 10k ohm entre Gate y GND de potencia.
* Drain del MOSFET -> Pin negativo del encendedor pirotécnico (E-Match).

## 3. Compilación y Carga de Firmware (PlatformIO)
Para compilar y subir el código a la Teensy 4.1:
./venv/bin/pio run -t upload -e teensy41
