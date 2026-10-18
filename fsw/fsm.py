from enum import Enum

class FlightState(Enum):
    PAD_IDLE = 1
    BOOST = 2
    COASTING = 3
    APOGEE_DETECTION = 4
    DROGUE_DESCENT = 5
    MAIN_DESCENT = 6
    LANDED = 7

class RocketFSM:
    def __init__(self):
        self.state = FlightState.PAD_IDLE
        self.apogee_altitude = 0.0

    def update(self, accel_z, altitude, vertical_velocity):
        if self.state == FlightState.PAD_IDLE and accel_z > 2.0:
            self.state = FlightState.BOOST
            
        elif self.state == FlightState.BOOST and accel_z < 0.0:
            self.state = FlightState.COASTING
            
        elif self.state == FlightState.COASTING and vertical_velocity <= 0.5:
            # Detección de apogeo: velocidad vertical cercana a cero o negativa
            self.state = FlightState.APOGEE_DETECTION
            self.apogee_altitude = altitude
            print(f"[PYRO] ¡APOGEO DETECTADO A {altitude:.2f}m! Disparando carga Drogue...")
            self.state = FlightState.DROGUE_DESCENT
            
        elif self.state == FlightState.DROGUE_DESCENT and altitude <= 100.0:
            print(f"[PYRO] Altitud de 100m alcanzada. Desplegando Paracaídas Principal (Main)...")
            self.state = FlightState.MAIN_DESCENT
            
        elif self.state == FlightState.MAIN_DESCENT and abs(vertical_velocity) < 0.5 and altitude < 5.0:
            self.state = FlightState.LANDED
            print(f"[LANDED] Cohete aterrizado con éxito.")
