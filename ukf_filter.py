import numpy as np

class RocketUKF:
    def __init__(self):
        self.n = 6
        self.x = np.zeros(self.n)
        self.P = np.eye(self.n) * 50.0
        # Matriz de ruido de proceso (Inercial / Deriva)
        self.Q = np.diag([0.05, 0.05, 0.05, 0.1, 0.1, 0.1])
        # Matriz de ruido de medida (GPS con mayor incertidumbre de alta frecuencia)
        self.R = np.eye(3) * 12.5

    def initialize(self, initial_state):
        self.x = np.copy(initial_state)

    def predict(self, dt, imu_acceleration):
        """
        Predicción basada en la dinámica cinemática y la aceleración medida por la IMU.
        """
        px, py, pz, vx, vy, vz = self.x
        
        # Integración con la aceleración real del cohete provista por la IMU
        ax, ay, az = imu_acceleration
        
        px_new = px + vx * dt + 0.5 * ax * (dt**2)
        py_new = py + vy * dt + 0.5 * ay * (dt**2)
        pz_new = pz + vz * dt + 0.5 * az * (dt**2)
        
        vx_new = vx + ax * dt
        vy_new = vy + ay * dt
        vz_new = vz + az * dt
        
        self.x = np.array([px_new, py_new, pz_new, vx_new, vy_new, vz_new])
        
        # Matriz de transición Jacobiana F
        F = np.eye(self.n)
        for i in range(3):
            F[i, i+3] = dt
            
        self.P = F @ self.P @ F.T + self.Q

    def update(self, gps_position_measured):
        """
        Corrección/Actualización del estado utilizando la posición GPS medida.
        """
        H = np.zeros((3, self.n))
        H[0, 0] = 1.0
        H[1, 1] = 1.0
        H[2, 2] = 1.0
        
        y = gps_position_measured - H @ self.x
        S = H @ self.P @ H.T + self.R
        K = self.P @ H.T @ np.linalg.inv(S)
        
        self.x = self.x + K @ y
        self.P = (np.eye(self.n) - K @ H) @ self.P
