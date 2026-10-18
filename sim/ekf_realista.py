import numpy as np
import time

class FiltroKalmanExtendido1D:
    def __init__(self):
        # Estado: [Altitud, Velocidad]
        self.x = np.array([0.0, 0.0])
        
        # Matriz de covarianza del error (Incertidumbre)
        self.P = np.eye(2) * 1.0
        
        # Ruido del proceso (incertidumbre del modelo físico)
        self.Q = np.array([[0.01, 0.0], [0.0, 0.1]])
        
        # Ruido de la medición (incertidumbre del barómetro BMP280)
        self.R = np.array([[0.5]])
        
        # Matriz de observación (medimos altitud)
        self.H = np.array([[1.0, 0.0]])
        
    def predecir(self, dt, aceleracion):
        # Modelo físico: x_{k} = F * x_{k-1} + B * u
        F = np.array([[1.0, dt], [0.0, 1.0]])
        B = np.array([[0.5 * dt**2], [dt]])
        
        # Predicción de estado
        self.x = F @ self.x + (B.flatten() * aceleracion)
        
        # Predicción de covarianza
        self.P = F @ self.P @ F.T + self.Q
        
    def actualizar(self, z_medido):
        # Innovación (residuo entre medición y predicción)
        y = z_medido - (self.H @ self.x)
        
        # Covarianza de la innovación
        S = self.H @ self.P @ self.H.T + self.R
        
        # Ganancia de Kalman
        K = self.P @ self.H.T @ np.linalg.inv(S)
        
        # Actualización de estado
        self.x = self.x + (K @ y)
        
        # Actualización de covarianza
        I = np.eye(2)
        self.P = (I - K @ self.H) @ self.P
        
        return self.x[0], self.x[1]

def ejecutar_ekf_realista():
    print("[INICIO] Simulando vuelo con ruido y filtrado EKF en tiempo real...")
    
    dt = 0.1
    ekf = FiltroKalmanExtendido1D()
    
    tiempo_motor = 2.0
    empuje_nominal = 15.0
    altitud_real = 0.0
    velocidad_real = 0.0
    
    for i in range(51):
        tiempo = i * dt
        
        # 1. Simulación física real con perturbaciones
        if tiempo <= tiempo_motor:
            acel_motor = empuje_nominal + np.random.normal(0, 0.5)
        else:
            acel_motor = 0.0
            
        acel_real = acel_motor - 9.81 + np.random.normal(0, 0.3)
        velocidad_real += acel_real * dt
        altitud_real += velocidad_real * dt
        if altitud_real < 0: 
            altitud_real = 0.0
            velocidad_real = 0.0

        # 2. Sensores sucios (ruido de hardware)
        acel_medida_imu = acel_real + np.random.normal(0, 0.2)
        altitud_medida_baro = altitud_real + np.random.normal(0, 0.5) # Ruido fuerte
        
        # 3. Aplicación del Filtro de Kalman Extendido
        ekf.predecir(dt, acel_medida_imu)
        alt_estimada, vel_estimada = ekf.actualizar(altitud_medida_baro)
        
        print(f"T: {tiempo:.1f}s | Real: {altitud_real:5.2f}m | Baro (Sucio): {altitud_medida_baro:5.2f}m | EKF (Limpio): {alt_estimada:5.2f}m")
        time.sleep(0.05)
        
    print("[FIN] Prueba de EKF realista completada con éxito.")

if __name__ == "__main__":
    ejecutar_ekf_realista()
