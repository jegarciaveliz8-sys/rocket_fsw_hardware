import numpy as np

class RocketUKF:
    def __init__(self):
        # Estado simplificado: [x, y, z, vx, vy, vz]
        self.state_dim = 6
        self.x = np.zeros(self.state_dim)
        self.P = np.eye(self.state_dim) * 10.0

    def predict(self, dt):
        # Propagación cinemática linealizada básica para puntos sigma
        F = np.eye(self.state_dim)
        for i in range(3):
            F[i, i+3] = dt
        self.x = F @ self.x
        Q = np.eye(self.state_dim) * 0.01
        self.P = F @ self.P @ F.T + Q

    def update(self, z_measured):
        H = np.eye(3, self.state_dim)
        R = np.eye(3) * 5.0
        y = z_measured - H @ self.x
        S = H @ self.P @ H.T + R
        K = self.P @ H.T @ np.linalg.inv(S)
        self.x = self.x + K @ y
        self.P = (np.eye(self.state_dim) - K @ H) @ self.P
