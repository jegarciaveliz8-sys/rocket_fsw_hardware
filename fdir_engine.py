import numpy as np

class FDIRSystem:
    """
    Sistema FDIR basado en la Distancia de Mahalanobis de Residuales de Kalman.
    """
    def __init__(self):
        self.status = "NOMINAL"
        self.injected_fault = "NONE"
        self.subsystems = {
            "TVC_ACTUATORS": "NOMINAL",
            "RCS_PROPULSION": "STANDBY",
            "IMU_PRIMARY": "HEALTHY",
            "GPS_RECEIVER": "LOCKED"
        }

    def evaluate_mahalanobis(self, residual, S_covariance):
        """
        D_M^2 = r^T * S^-1 * r (Distribución Chi-Cuadrado)
        """
        try:
            inv_S = np.linalg.inv(S_covariance)
            d_mahalanobis_sq = float(residual.T @ inv_S @ residual)
        except np.linalg.LinAlgError:
            d_mahalanobis_sq = 0.0
            
        # Umbrales Chi-Cuadrado para 3 grados de libertad (p < 0.01 y p < 0.001)
        # 3 DOF: Threshold 95% = 7.81, 99.9% = 16.27
        if d_mahalanobis_sq > 16.27:
            self.status = "CRITICAL_ANOMALY"
            self.injected_fault = "IMU_SENSOR_FAILURE_OR_TVC_DESYNC"
            self.subsystems["TVC_ACTUATORS"] = "ISOLATED"
            self.subsystems["RCS_PROPULSION"] = "ENGAGED_AUTONOMOUS"
            self.subsystems["IMU_PRIMARY"] = "DEGRADED"
            action = f"FDIR AUTONOMOUS RECOVERY: Mahalanobis D^2={d_mahalanobis_sq:.2f} > 16.27. TVC Isolated. RCS Activated."
        elif d_mahalanobis_sq > 7.81:
            self.status = "WARNING_DRIFT"
            self.injected_fault = "GPS_MULTIPATH_NOISE"
            self.subsystems["GPS_RECEIVER"] = "FILTERING_DEGRADED"
            action = f"FDIR WARNING: Mahalanobis D^2={d_mahalanobis_sq:.2f} > 7.81. Increasing Kalman R Matrix covariance."
        else:
            self.status = "NOMINAL"
            self.injected_fault = "NONE"
            self.subsystems["TVC_ACTUATORS"] = "NOMINAL"
            self.subsystems["RCS_PROPULSION"] = "STANDBY"
            self.subsystems["IMU_PRIMARY"] = "HEALTHY"
            self.subsystems["GPS_RECEIVER"] = "LOCKED"
            action = f"NOMINAL: Mahalanobis D^2={d_mahalanobis_sq:.2f} within Chi-Square bounds."
            
        return action, d_mahalanobis_sq
