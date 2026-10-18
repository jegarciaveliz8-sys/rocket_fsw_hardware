import numpy as np

class RocketEKF:
    def __init__(self):
        # Estado inicial [posición, velocidad]
        self.x = np.array([[0.0], [0.0]])
        # Matriz de covarianza del error
        self.P = np.array([[1.0, 0.0], [0.0, 1.0]])
        # Matriz de transición de estado (dt = 1s)
        self.F = np.array([[1.0, 1.0], [0.0, 1.0]])
        # Ruido del proceso
        self.Q = np.array([[0.01, 0.0], [0.0, 0.1]])
        # Ruido de la medición del sensor
        self.R = np.array([[5.0]])
        # Matriz de observación
        self.H = np.array([[1.0, 0.0]])

    def predict(self):
        self.x = np.dot(self.F, self.x)
        self.P = np.dot(np.dot(self.F, self.P), self.F.T) + self.Q
        return self.x[0, 0], self.x[1, 0]

    def update(self, z_measurement):
        # Innovación / Residual
        y = np.array([[z_measurement]]) - np.dot(self.H, self.x)
        S = np.dot(np.dot(self.H, self.P), self.H.T) + self.R
        # Ganancia de Kalman
        K = np.dot(np.dot(self.P, self.H.T), np.linalg.inv(S))
        # Actualizar estado estimado
        self.x = self.x + np.dot(K, y)
        self.P = np.dot((np.eye(2) - np.dot(K, self.H)), self.P)
        return self.x[0, 0], self.x[1, 0]
