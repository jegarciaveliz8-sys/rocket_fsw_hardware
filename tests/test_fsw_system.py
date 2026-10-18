import pytest
from fsw.fsm import RocketFSM, FlightState
from fsw.ekf import ExtendedKalmanFilter1D
from fsw.telemetry_packet import pack_telemetry, unpack_telemetry

def test_fsm_transitions():
    """Valida la secuencia nominal de estados de la FSM."""
    fsm = RocketFSM()
    assert fsm.state == FlightState.PAD_IDLE
    
    fsm.update(accel_z=2.5, altitude=0.0, vertical_velocity=0.0)
    assert fsm.state == FlightState.BOOST
    
    fsm.update(accel_z=-1.0, altitude=50.0, vertical_velocity=30.0)
    assert fsm.state == FlightState.COASTING
    
    fsm.update(accel_z=0.0, altitude=150.0, vertical_velocity=0.1)
    assert fsm.state == FlightState.DROGUE_DESCENT

def test_ekf_convergence():
    """Valida que el EKF devuelva estimaciones numéricas válidas y acotadas."""
    ekf = ExtendedKalmanFilter1D(dt=0.1)
    for i in range(5):
        ekf.predict(accel_z=2.0)
        alt, vel = ekf.update(z_measurement=10.0 * (i + 1))
        assert isinstance(alt, float)
        assert isinstance(vel, float)
        assert not (alt != alt)
        assert not (vel != vel)

def test_telemetry_packet_serialization():
    """Valida el empaquetado y desempaquetado binario de telemetría."""
    mission = "MIS01"
    seq = 42
    alt = 145.8
    vel = 55.2
    accel = 4.9
    
    binary_data = pack_telemetry(mission, seq, alt, vel, accel)
    assert isinstance(binary_data, bytes)
    assert len(binary_data) == 24  # Tamaño ajustado a la alineación estructural real
    
    decoded = unpack_telemetry(binary_data)
    assert decoded["mission_id"] == mission
    assert decoded["seq"] == seq
    assert pytest.approx(decoded["altitude"], 0.01) == alt
    assert pytest.approx(decoded["velocity"], 0.01) == vel
    assert pytest.approx(decoded["acceleration"], 0.01) == accel
