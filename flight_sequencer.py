import numpy as np

class FlightSequencer:
    """
    Máquina de Estados Finitos (FSM) con gestión de aborto y perfiles de guía de lanzamiento.
    """
    def __init__(self):
        self.state = "T_MINUS_COUNTDOWN"
        self.abort_mode = False
        self.met = 0.0  # Mission Elapsed Time
        self.staging_status = {"stage_1": "ACTIVE", "stage_2": "STANDBY", "fairing": "ATTACHED"}

    def evaluate_fsm(self, alt_m, speed_ms, dynamic_pressure_pa, fdir_status):
        self.met += 1.0

        # Lógica crítica de Aborto por FDIR o Presión Anómala
        if fdir_status == "CRITICAL_ANOMALY" and self.state not in ["ORBITAL_INSERTION", "NOMINAL_LEO"]:
            self.state = "ABORT_MISSION_LES_TRIGGERED"
            self.abort_mode = True
            return self.state, self.met

        if self.state == "T_MINUS_COUNTDOWN" and speed_ms > 1.0:
            self.state = "LIFTOFF"
        elif self.state == "LIFTOFF" and alt_m > 10000.0 and dynamic_pressure_pa > 35000:
            self.state = "MAX_Q_TRANSITION"
        elif self.state == "MAX_Q_TRANSITION" and alt_m > 45000.0:
            self.state = "MAIN_ENGINE_CUTOFF_MECO"
            self.staging_status["stage_1"] = "JETTISONED"
            self.staging_status["fairing"] = "DEPLOYED"
        elif self.state == "MAIN_ENGINE_CUTOFF_MECO" and alt_m > 120000.0:
            self.state = "STAGE_2_IGNITION"
            self.staging_status["stage_2"] = "ACTIVE"
        elif self.state == "STAGE_2_IGNITION" and alt_m >= 395000.0:
            self.state = "NOMINAL_LEO_ORBIT"
            
        return self.state, self.met
