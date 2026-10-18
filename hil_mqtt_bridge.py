import numpy as np
import threading
import json

class HardwareInTheLoopBridge:
    """
    Puente de comunicaciones HIL concurrente con calibración de sensores físicos.
    """
    def __init__(self):
        self.lock = threading.Lock()
        self.operational_mode = "VIRTUAL_SIMULATION"
        
        # Matriz de calibración y alineación ortogonal de IMU (3x3)
        self.T_calibration = np.array([
            [1.002, 0.001, -0.0005],
            [0.000, 0.999,  0.0012],
            [0.001, 0.000,  1.0010]
        ])
        self.sensor_bias = np.array([0.015, -0.008, 0.021]) # m/s^2
        self.raw_hardware_packet = {"ax": 0.0, "ay": 0.0, "az": 9.81}

    def process_incoming_hardware_stream(self, raw_json_payload: str) -> bool:
        """Procesa y calibra tramas crudas provenientes de telemetría IoT física."""
        try:
            data = json.loads(raw_json_payload)
            with self.lock:
                raw_accel = np.array([float(data.get("ax", 0)), float(data.get("ay", 0)), float(data.get("az", 9.81))])
                
                # Aplicación de matriz de calibración y compensación de sesgo en tiempo real
                calibrated_accel = self.T_calibration @ raw_accel - self.sensor_bias
                
                self.raw_hardware_packet = {
                    "ax": round(float(calibrated_accel[0]), 4),
                    "ay": round(float(calibrated_accel[1]), 4),
                    "az": round(float(calibrated_accel[2]), 4)
                }
                self.operational_mode = "HIL_HARDWARE_CONNECTED"
            return True
        except Exception:
            return False

    def get_calibrated_acceleration(self):
        with self.lock:
            return self.raw_hardware_packet, self.operational_mode
