import numpy as np

class FDIRSystem:
    def __init__(self):
        self.status = "NOMINAL"
        self.injected_fault = "NONE"
        self.fault_history = []
        
        # Umbrales estadísticos de desviación de residuos
        self.warning_threshold_sigma = 2.5
        self.critical_threshold_sigma = 4.0
        
        # Matriz de estado de subsistemas para reconfiguración autónoma
        self.subsystems = {
            "TVC_PRIMARY": "NOMINAL",
            "RCS_BACKUP": "STANDBY",
            "PROPULSION_VALVES": "NOMINAL",
            "IMU_REDUNDANCY": "ACTIVE"
        }

    def evaluate_telemetry(self, state_real, state_estimated, covariance_matrix=None):
        """
        Calcula la distancia de residuos entre la física estimada y la telemetría recibida.
        Ejecuta el aislamiento de fallas y activa procedimientos de recuperación en tiempo real.
        """
        residual_vector = state_real[:3] - state_estimated[:3]
        euclidean_residual = np.linalg.norm(residual_vector)
        
        # Usar covarianza o estimación de varianza estándar (sigma ~ 15.0m)
        sigma = 15.0
        sigma_deviation = euclidean_residual / sigma

        action = "SYSTEM_OPERATIONAL_NOMINAL"

        if sigma_deviation > self.critical_threshold_sigma:
            self.status = "CRITICAL_ANOMALY"
            self.injected_fault = "THRUST_VECTOR_DEGRADATION"
            
            # Reconfiguración Autónoma de Emergencia
            self.subsystems["TVC_PRIMARY"] = "DEGRADED_ISOLATED"
            self.subsystems["RCS_BACKUP"] = "ACTIVE_ENGAGED"
            
            action = "AUTO_RECOVERY: PRIMARY TVC ISOLATED -> RCS THRUS-VECTOR ENGAGED [REBALANCING THRUST 85%]"
            self.fault_history.append({"severity": "CRITICAL", "action": action})

        elif sigma_deviation > self.warning_threshold_sigma:
            self.status = "WARNING_DRIFT"
            self.injected_fault = "IMU_SENSOR_BIAS_DETECTED"
            
            # Reconfiguración de sensores
            self.subsystems["IMU_REDUNDANCY"] = "RECALIBRATING"
            action = "AUTO_CORRECTION: RECALIBRATING IMU BIAS VIA GNSS COVARIANCE"
            self.fault_history.append({"severity": "WARNING", "action": action})

        else:
            self.status = "NOMINAL"
            self.injected_fault = "NONE"
            self.subsystems["TVC_PRIMARY"] = "NOMINAL"
            self.subsystems["RCS_BACKUP"] = "STANDBY"
            action = "NOMINAL: NO FAULT ISOLATION REQUIRED"

        return action
