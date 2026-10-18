import numpy as np

class RocketUKF:
    """
    Unscented Kalman Filter para Estimación de Posición, Velocidad y Sesgo de IMU.
    Estado x (9D): [px, py, pz, vx, vy, vz, bias_ax, bias_ay, bias_az]
    """
    def __init__(self):
        self.n = 9
        self.x = np.zeros(self.n)
        self.P = np.eye(self.n) * 100.0
        
        # Parámetros Unscented Transformation (Julier-Uhlmann / Van der Merwe)
        self.alpha = 1e-3
        self.beta = 2.0
        self.kappa = 0.0
        self.lambda_ = (self.alpha**2) * (self.n + self.kappa) - self.n
        
        # Pesos de Sigma Points
        self.Wm = np.zeros(2 * self.n + 1)
        self.Wc = np.zeros(2 * self.n + 1)
        
        self.Wm[0] = self.lambda_ / (self.n + self.lambda_)
        self.Wc[0] = self.Wm[0] + (1.0 - self.alpha**2 + self.beta)
        
        for i in range(1, 2 * self.n + 1):
            self.Wm[i] = 0.5 / (self.n + self.lambda_)
            self.Wc[i] = self.Wm[i]
            
        self.Q = np.diag([0.01]*3 + [0.05]*3 + [1e-5]*3)
        self.R = np.diag([10.0]*3)  # Varianza de ruido GPS (m^2)

    def initialize(self, initial_state_6d):
        self.x[:6] = initial_state_6d
        self.x[6:] = 0.0  # Sesgo inicial nulo

    def generate_sigma_points(self):
        sigma_points = np.zeros((2 * self.n + 1, self.n))
        sigma_points[0] = self.x
        
        # Raíz cuadrada de la matriz de covarianza (Cholesky)
        try:
            L = np.linalg.cholesky((self.n + self.lambda_) * self.P)
        except np.linalg.LinAlgError:
            # SVD de respaldo si la matriz pierde definición positiva
            U, S, Vt = np.linalg.svd(self.P)
            L = U @ np.diag(np.sqrt(np.maximum(S, 1e-9)))
            
        for i in range(self.n):
            sigma_points[i + 1]          = self.x + L[:, i]
            sigma_points[i + 1 + self.n] = self.x - L[:, i]
            
        return sigma_points

    def predict(self, dt, imu_accel):
        sigmas = self.generate_sigma_points()
        sigmas_fwd = np.zeros_like(sigmas)
        
        for i in range(2 * self.n + 1):
            pos = sigmas[i, :3]
            vel = sigmas[i, 3:6]
            bias_a = sigmas[i, 6:]
            
            # Aceleración corregida por el sesgo estimado
            a_corr = imu_accel - bias_a
            
            pos_next = pos + vel * dt + 0.5 * a_corr * (dt**2)
            vel_next = vel + a_corr * dt
            
            sigmas_fwd[i, :3] = pos_next
            sigmas_fwd[i, 3:6] = vel_next
            sigmas_fwd[i, 6:] = bias_a  # Modelo de paseo aleatorio para el sesgo
            
        # Reconstruir media y covarianza predicha
        self.x = np.sum(self.Wm[:, np.newaxis] * sigmas_fwd, axis=0)
        
        self.P = np.zeros((self.n, self.n))
        for i in range(2 * self.n + 1):
            diff = (sigmas_fwd[i] - self.x)[:, np.newaxis]
            self.P += self.Wc[i] * (diff @ diff.T)
        self.P += self.Q

    def update(self, gps_pos_measured):
        sigmas = self.generate_sigma_points()
        Z_sigmas = sigmas[:, :3]  # Función de observación h(x) = posición
        
        z_mean = np.sum(self.Wm[:, np.newaxis] * Z_sigmas, axis=0)
        
        S = np.zeros((3, 3))
        Pxz = np.zeros((self.n, 3))
        
        for i in range(2 * self.n + 1):
            z_diff = (Z_sigmas[i] - z_mean)[:, np.newaxis]
            x_diff = (sigmas[i] - self.x)[:, np.newaxis]
            
            S += self.Wc[i] * (z_diff @ z_diff.T)
            Pxz += self.Wc[i] * (x_diff @ z_diff.T)
            
        S += self.R
        
        # Ganancia de Kalman K
        K = Pxz @ np.linalg.inv(S)
        residual = gps_pos_measured - z_mean
        
        self.x += K @ residual
        self.P -= K @ S @ K.T
        
        return residual, S
