import numpy as np

class FlightEKF:
    def __init__(self):
        # Estado: [Altitud, Velocidad]
        self.x = np.array([[0.0], [0.0]])
        # Covarianza de estimación
        self.P = np.eye(2) * 1.0
        # Ruido del proceso
        self.Q = np.array([[0.001, 0.0], [0.0, 0.003]])
        # Ruido de la medición (IMU / GPS)
        self.R = np.array([[0.05]])

    def predict(self, dt: float, acceleration: float):
        # Modelo de movimiento linealizado
        F = np.array([[1.0, dt], [0.0, 1.0]])
        B = np.array([[0.5 * dt**2], [dt]])
        
        self.x = F @ self.x + B * acceleration
        self.P = F @ self.P @ F.T + self.Q

    def update(self, z_measured: float):
        # Matriz de observación
        H = np.array([[1.0, 0.0]])
        y = z_measured - (H @ self.x)[0, 0]
        S = H @ self.P @ H.T + self.R
        K = self.P @ H.T / S
        
        self.x = self.x + K * y
        self.P = (np.eye(2) - K @ H) @ self.P
        
        return float(self.x[0, 0]), float(self.x[1, 0])
