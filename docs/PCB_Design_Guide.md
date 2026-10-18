# Guía de Interconexiones PCB - Rocket Flight Computer v1.0

## 1. Asignación de Pines Teensy 4.1
- **I2C Bus 0:**
  - `SDA` -> Pin 18 (Conectar a MPU6050 y BMP280 con resistencias Pull-up de 4.7kΩ)
  - `SCL` -> Pin 19 (Conectar a MPU6050 y BMP280)
- **Canal de Pirotecnia:**
  - `PYRO_TRIGGER` -> Pin 23 (Señal Digital 3.3V hacia el Gate del MOSFET)
- **Ranura MicroSD:**
  - Utiliza los pines integrados de la ranura nativa SDIO de la Teensy 4.1 (`BUILTIN_SDCARD`).

## 2. Esquemático del Canal de Ignición Pirotécnica

Teensy Pin 23 ---> [Resistencia 220 Ohm] ---> Gate MOSFET (IRLZ44N)
                                                 |
                                     Source ---> GND Común
                                                 |
Batería LiPo 7.4V (+)---> [E-Match] ---> Drain MOSFET

## 3. Lista de Componentes (BOM)
1. **Teensy 4.1** (Microcontrolador Principal)
2. **MPU6050** (Acelerómetro/Giroscopio)
3. **BMP280** (Barómetro de Precisión)
4. **MOSFET IRLZ44N** (Conmutación de Alta Corriente N-Channel)
5. **Diodo 1N4007** (Protección contra retorno inductivo)
6. **Resistencia 10kΩ** (Pull-Down para la compuerta del MOSFET)
7. **Regulador Buck 5V 3A** (Alimentación limpia para la Teensy desde la batería de 7.4V)
