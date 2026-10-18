import numpy as np

MU = 3.986004418e14  # m^3/s^2
R_EARTH = 6378137.0  # m

def cartesian_to_keplerian(r_vec, v_vec):
    """Convierte vector de estado cartesiano (ECI) a Elementos Keplerianos clásicos."""
    r = np.linalg.norm(r_vec)
    v = np.linalg.norm(v_vec)
    h_vec = np.cross(r_vec, v_vec)
    h = np.linalg.norm(h_vec)
    
    inclination = np.arccos(h_vec[2] / h)
    
    # Energía orbital específica
    energy = (v**2 / 2.0) - (MU / r)
    semi_major_axis = -MU / (2.0 * energy) if energy != 0 else float('inf')
    
    # Excentricidad
    e_vec = ((v**2 - MU/r) * r_vec - np.dot(r_vec, v_vec) * v_vec) / MU
    eccentricity = np.linalg.norm(e_vec)
    
    return {
        "semi_major_axis_km": round(semi_major_axis / 1000.0, 3),
        "eccentricity": round(eccentricity, 6),
        "inclination_deg": round(np.degrees(inclination), 3)
    }

def calculate_optimal_burn(r_current_vec, v_current_vec, target_altitude_km):
    """Calcula el vector de empuje Delta-V y la maniobra de transferencia coplanar."""
    r_current = np.linalg.norm(r_current_vec)
    r_target = R_EARTH + (target_altitude_km * 1000.0)
    
    # Transferencia Hohmann de alta precisión vectorial
    a_trans = (r_current + r_target) / 2.0
    v_curr_mag = np.linalg.norm(v_current_vec)
    
    v_perigee = np.sqrt(MU * (2.0 / r_current - 1.0 / a_trans))
    dv_magnitude = abs(v_perigee - v_curr_mag)
    
    # Vector de dirección de quemado alineado con la velocidad tangencial
    dv_vector = (v_current_vec / v_curr_mag) * dv_magnitude
    
    return {
        "dv_magnitude_m_s": round(float(dv_magnitude), 3),
        "dv_vector_xyz": [round(float(x), 3) for x in dv_vector],
        "target_semi_major_axis_km": round(a_trans / 1000.0, 3)
    }
