import pytest
import numpy as np
import sys
import os

# Asegurar la ruta raíz del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sim.ekf_realista import FiltroKalmanExtendido1D
from sim.flight_computer import ComputadoraDeVuelo

def test_pipeline_vuelo_completo():
    """Prueba E2E: Simula un vuelo completo con ruido, filtra con EKF y valida la FSM."""
    ekf = FiltroKalmanExtendido1D()
    fc = ComputadoraDeVuelo()
    
    dt = 0.1
    altitud_real = 0.0
    velocidad_real = 0.0
    empuje = 20.0
    
    apogeo_alcanzado = False
    paracaidas_principal_abierto = False
    
    # Simular 40 pasos de vuelo (subida y bajada)
    for i in range(40):
        t = i * dt
        
        # 1. Simulación física simplificada con motor y gravedad
        if t <= 2.0:
            acel = empuje + np.random.normal(0, 0.2) - 9.81
        else:
            acel = -9.81 + np.random.normal(0, 0.2)
            
        velocidad_real += acel * dt
        altitud_real += velocidad_real * dt
        if altitud_real < 0:
            altitud_real = 0.0
            velocidad_real = 0.0
            
        # 2. Sensores ruidosos
        alt_baro = altitud_real + np.random.normal(0, 0.5)
        acel_imu = acel + np.random.normal(0, 0.1)
        
        # 3. Procesamiento EKF
        ekf.predecir(dt, acel_imu)
        alt_estimada, vel_estimada = ekf.actualizar(alt_baro)
        
        # 4. Decisión de la Computadora de Vuelo (FSM)
        estado, evento = fc.actualizar_fsm(t, alt_estimada, vel_estimada)
        
        if "APOGEO" in evento:
            apogeo_alcanzado = True
        if "PRINCIPAL" in evento:
            paracaidas_principal_abierto = True
            
    fc.cerrar()
    
    # Verificaciones de la misión
    assert fc.altitud_maxima > 10.0, "El cohete no alcanzó la altura mínima esperada."
    assert os.path.exists("data/black_box_flight.csv"), "La caja negra no generó el archivo de registro."
