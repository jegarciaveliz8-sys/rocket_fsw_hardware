import numpy as np
import time

class SimuladorVueloRealista:
    def __init__(self):
        # Parámetros iniciales del cohete
        self.altitud = 0.0
        self.velocidad = 0.0
        self.aceleracion = 0.0
        self.tiempo = 0.0
        self.dt = 0.1  # 10 Hz
        
        # Estado del motor (fase de impulso de 2 segundos)
        self.tiempo_motor = 2.0
        self.empuje_nominal = 15.0  # m/s^2 de aceleración neta por motor
        
    def simular_paso(self, i):
        self.tiempo = i * self.dt
        
        # 1. Simulación de Empuje y Gravedad con ráfaga de viento aleatoria
        if self.tiempo <= self.tiempo_motor:
            # Empuje del motor + ruido de combustión
            acel_motor = self.empuje_nominal + np.random.normal(0, 0.5)
        else:
            acel_motor = 0.0
            
        gravedad = -9.81
        viento_turbulento = np.random.normal(0, 0.3)  # Ráfagas laterales/verticales
        
        # Aceleración real combinada
        self.aceleracion = acel_motor + gravedad + viento_turbulento
        
        # Integración numérica (Euler)
        self.velocidad += self.aceleracion * self.dt
        self.altitud += self.velocidad * self.dt
        
        if self.altitud < 0:
            self.altitud = 0.0
            self.velocidad = 0.0

        # 2. Simulación de Ruido en Sensores (Hardware real imperfecto)
        # Barómetro BMP280: ruido de +/- 0.5 metros
        altitud_medida_baro = self.altitud + np.random.normal(0, 0.5)
        
        # Acelerómetro MPU6050: ruido de vibración de alta frecuencia
        acel_medida_imu = self.aceleracion + np.random.normal(0, 0.2)
        
        return {
            "tiempo": round(self.tiempo, 2),
            "altitud_real": round(self.altitud, 2),
            "altitud_baro": round(altitud_medida_baro, 2),
            "acel_imu": round(acel_medida_imu, 2)
        }

def ejecutar_prueba_realista():
    print("[INICIO] Ejecutando simulación aeroespacial con ruido y perturbaciones reales...")
    sim = SimuladorVueloRealista()
    
    # Simular 50 pasos (5 segundos de vuelo)
    for i in range(51):
        datos = sim.simular_paso(i)
        print(f"T: {datos['tiempo']}s | Alt. Real: {datos['altitud_real']}m | Barómetro (Con Ruido): {datos['altitud_baro']}m | IMU Z: {datos['acel_imu']}m/s²")
        time.sleep(0.05)
        
    print("[FIN] Simulación realista completada con éxito. El Filtro de Kalman procesaría estos datos sucios.")

if __name__ == "__main__":
    ejecutar_prueba_realista()
