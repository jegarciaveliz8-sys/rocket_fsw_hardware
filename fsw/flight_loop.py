from fsw.ekf import ExtendedKalmanFilter1D
import random
import time

def run_ekf_test():
    ekf = ExtendedKalmanFilter1D(dt=0.1)
    print("Iniciando simulación del Filtro de Kalman Extendido (EKF)...")
    
    true_alt = 0.0
    for i in range(10):
        # Simular aceleración y lectura barométrica ruidosa
        accel = 5.8 if i < 5 else -1.0
        true_alt += 10.0 * i
        noisy_baro = true_alt + random.uniform(-3.0, 3.0)
        
        ekf.predict(accel_z=accel)
        filt_alt, filt_vel = ekf.update(noisy_baro)
        
        print(f"Paso {i}: Barómetro Ruidoso={noisy_baro:.1f}m | EKF Altitud={filt_alt:.1f}m | EKF Velocidad={filt_vel:.1f}m/s")
        time.sleep(0.05)

if __name__ == "__main__":
    run_ekf_test()
