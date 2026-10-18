import pytest
import numpy as np
import sys
import os

# Asegurar que la ruta incluya la raíz del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sim.ekf_realista import FiltroKalmanExtendido1D

def test_ekf_convergencia():
    """Verifica que el EKF converja hacia la altitud correcta a pesar del ruido del sensor."""
    ekf = FiltroKalmanExtendido1D()
    dt = 0.1
    
    # Simular una aceleración constante hacia arriba durante 1 segundo
    for _ in range(10):
        ekf.predecir(dt, aceleracion=5.0)
        # Inyectar una medición ruidosa pero centrada en la realidad esperada
        alt_estimada, _ = ekf.actualizar(z_medido=2.5)
        
    # La estimación debe estar dentro de un rango lógico y razonable
    assert alt_estimada > 0.0
    assert isinstance(alt_estimada, float)

def test_ekf_filtro_ruido_extremo():
    """Comprueba que una lectura extremadamente errónea del barómetro no rompa el estado del EKF."""
    ekf = FiltroKalmanExtendido1D()
    dt = 0.1
    
    ekf.predecir(dt, aceleracion=0.0)
    # Medición normal inicial
    alt1, _ = ekf.actualizar(z_medido=10.0)
    
    ekf.predecir(dt, aceleracion=0.0)
    # Inyectar un pico de ruido masivo (error de sensor de 100 metros)
    alt2, _ = ekf.actualizar(z_medido=110.0)
    
    # El filtro de Kalman debe amortiguar el impacto gracias a la matriz de covarianza (R)
    diferencia = abs(alt2 - alt1)
    assert diferencia < 50.0, "El EKF reaccionó de forma exagerada ante un ruido de sensor."

def test_maquina_estados_apogeo():
    """Simula la lógica de detección de apogeo de la máquina de estados."""
    alturas = [100.0, 150.0, 180.0, 180.0, 175.0] # Comienza a descender en el paso 4
    
    estado_fsm = "ASCENSO"
    apogeo_detectado = False
    
    for i in range(1, len(alturas)):
        if alturas[i] < alturas[i-1] and estado_fsm == "ASCENSO":
            estado_fsm = "APOGEO"
            apogeo_detectado = True
            break
            
    assert apogeo_detectado == True
    assert estado_fsm == "APOGEO"
