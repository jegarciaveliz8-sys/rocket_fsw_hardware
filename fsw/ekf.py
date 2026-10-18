import numpy as np

class ExtendedKalmanFilter1D:
    def __init__(self, dt=0.01):
        self.dt = dt  # Intervalo de tiempo entre muestras (ej. 100 Hz = 0.01s)
        
        # Estado inicial [Posición, Velocidad, Aceleración]
        self.x = np.zeros((3, 1))
        
        # Matriz de covarianza del error de estimación (P)
        self.P = np.eye(3) * 10.0
        
        # Matriz de covarianza del ruido de proceso (Q)
        self.Q = np.array([
            [0.001, 0.0, 0.0],
            [0.0, 0.005, 0.0],
            [0.0, 0.0, 0.1]
        ])
        
        # Varianza del sensor barométrico (R)
        self.R = np.array([[2.0]]) # 2 metros de desviación estándar aproximada

    def predict(self, accel_z):
        dt = self.dt
        # Matriz de transición de estado (Modelo físico cinemático)
        # z_k = z_{k-1} + v*dt + 0.5*a*dt^2
        # v_k = v_{k-1} + a*dt
        # a_k = a_{k-1}
        F = np.array([
            [1.0, dt, 0.5 * dt**2],
            [0.0, 1.0, dt],
            [0.0, 0.0, 1.0]
        ])
        
        # Entrada de control u (aceleración medida por la IMU)
        B = np.array([
            [0.5 * dt**2],
            [dt],
            [1.0]
        ])
        
        u = np.array([[accel_z]])
        
        # Predicción del estado
        self.x = F @ self.x + B @ u
        # Predicción de la covarianza
        self.P = F @ self.P @ F.T + self.Q

    def update(self, z_measurement):
        # Matriz de observación (solo medimos posición/altitud con el barómetro)
        H = np.array([[1.0, 0.0, 0.0]])
        
        # Innovación (residuo)
        y = z_measurement - (H @ self.x)
        
        # Covarianza de la innovación
        S = H @ self.P @ H.T + self.R
        
        # Ganancia de Kalman
        K = self.P @ H.T @ np.linalg.inv(S)
        
        # Actualización del estado
        self.x = self.x + K @ y
        
        # Actualización de la covarianza
        I = np.eye(3)
        self.P = (I - K @ H) @ self.P
        
        return self.x[0, 0], self.x[1, 0] # Retorna altitud y velocidad filtradas
