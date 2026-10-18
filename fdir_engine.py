import numpy as np

class FDIRSystem:
    def __init__(self):
        self.status = "NOMINAL"
        self.injected_fault = "NONE"
        self.residual_threshold = 15.0

    def evaluate_telemetry(self, state_real, state_model):
        residual = np.linalg.norm(state_real - state_model)
        if residual > self.residual_threshold:
            self.status = "FAULT_DETECTED"
            if residual > 50.0:
                self.injected_fault = "CRITICAL_DRAG_OR_PROPULSION_ANOMALY"
                return "AUTO_RECOVERY: REDUCING THRUST / ACTIVATING RCS BACKUP"
            return "WARNING: HIGH RESIDUAL DRIFT"
        else:
            self.status = "NOMINAL"
            self.injected_fault = "NONE"
            return "SYSTEM NOMINAL"
