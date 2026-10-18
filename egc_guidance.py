import numpy as np

MU = 3.986004418e14  # m^3/s^2
R_EARTH = 6378137.0  # m

class ExplicitGuidanceComputer:
    """
    Computadora de Guía Explícita (EGC) - Ley de Dirección Tangencial Lineal (Linear Tangent Steering).
    Calcula el vector de orientación de empuje u(t) en tiempo real para inserción orbital precisa.
    """
    def __init__(self, target_altitude_km=400.0, target_velocity_ms=7670.0):
        self.r_target = R_EARTH + (target_altitude_km * 1000.0)
        self.v_target = target_velocity_ms
        self.t_go = 100.0  # Time-to-go estimado (s)

    def compute_steering_vector(self, current_pos: np.ndarray, current_vel: np.ndarray, isp=310.0, thrust_n=500000.0, mass_kg=50000.0):
        r_mag = np.linalg.norm(current_pos)
        v_mag = np.linalg.norm(current_vel)
        
        # Errores de estado respecto al objetivo
        delta_r = self.r_target - r_mag
        delta_v = self.v_target - v_mag
        
        # Estimación de aceleración de empuje disponible a_t
        a_t = thrust_n / mass_kg
        
        # Time-to-go iterativo (Ecuación de guía explícita)
        if a_t > 0:
            self.t_go = max(1.0, delta_v / a_t)
            
        # Parámetros de dirección tangencial lineal (a + b*t)
        # Orientación primaria a lo largo del vector progrado + corrección radial
        unit_vel = current_vel / v_mag if v_mag > 0 else np.array([0, 1, 0])
        unit_rad = current_pos / r_mag if r_mag > 0 else np.array([1, 0, 0])
        
        # Corrección de ángulo de elevación de empuje pitch (theta_p)
        gain_p = 0.05
        pitch_angle_rad = gain_p * (delta_r / self.r_target)
        
        # Vector unitario de actitud/empuje deseado u_thrust
        u_thrust = np.cos(pitch_angle_rad) * unit_vel + np.sin(pitch_angle_rad) * unit_rad
        u_thrust = u_thrust / np.linalg.norm(u_thrust)
        
        # Vector de delta-v remanente
        remaining_dv_vec = u_thrust * delta_v
        
        return {
            "time_to_go_sec": round(float(self.t_go), 2),
            "steering_unit_vector_xyz": [round(float(x), 4) for x in u_thrust],
            "pitch_correction_deg": round(float(np.degrees(pitch_angle_rad)), 3),
            "remaining_dv_ms": round(float(delta_v), 2),
            "guidance_status": "LOCKED_AUTO_GUIDANCE" if abs(delta_r) < 10000 else "CONVERGING"
        }
