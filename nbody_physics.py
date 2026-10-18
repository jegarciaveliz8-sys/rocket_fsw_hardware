import numpy as np

# Parámetros gravitacionales μ = G * M (m^3 / s^2)
MU_EARTH = 3.986004418e14
MU_MOON = 4.9048695e12
MU_SUN = 1.32712440018e20

# Radio aproximado de la Esfera de Influencia (SOI)
SOI_EARTH_M = 925000000.0  # ~925,000 km
SOI_MOON_M = 66100000.0    # ~66,100 km

def nbody_gravitational_acceleration(pos_eci, sim_time_sec):
    """
    Calcula la aceleración gravitacional vectorial de 3 cuerpos (Tierra, Luna, Sol) sobre el vehículo.
    """
    r_earth = np.linalg.norm(pos_eci)
    acc_earth = - (MU_EARTH / (r_earth**3)) * pos_eci if r_earth > 0 else np.zeros(3)
    
    # Posición aproximada de la Luna (Órbita a ~384,400 km)
    omega_moon = 2.6617e-6  # rad/s
    r_moon_orbit = 384400000.0
    pos_moon_eci = np.array([
        r_moon_orbit * np.cos(omega_moon * sim_time_sec),
        r_moon_orbit * np.sin(omega_moon * sim_time_sec),
        0.0
    ])
    
    pos_rel_moon = pos_eci - pos_moon_eci
    dist_moon = np.linalg.norm(pos_rel_moon)
    acc_moon = - (MU_MOON / (dist_moon**3)) * pos_rel_moon if dist_moon > 0 else np.zeros(3)
    
    # Posición aproximada del Sol (~1 AU)
    omega_sun = 1.990986e-7  # rad/s
    r_sun_orbit = 1.496e11
    pos_sun_eci = np.array([
        r_sun_orbit * np.cos(omega_sun * sim_time_sec),
        r_sun_orbit * np.sin(omega_sun * sim_time_sec),
        0.0
    ])
    pos_rel_sun = pos_eci - pos_sun_eci
    dist_sun = np.linalg.norm(pos_rel_sun)
    acc_sun = - (MU_SUN / (dist_sun**3)) * pos_rel_sun if dist_sun > 0 else np.zeros(3)
    
    # Determinación de la SOI dominante
    if dist_moon < SOI_MOON_M:
        soi_active = "MOON_SOI"
    elif r_earth < SOI_EARTH_M:
        soi_active = "EARTH_SOI"
    else:
        soi_active = "HELIOCENTRIC_SOI_MARS_BOUND"
        
    total_accel = acc_earth + acc_moon + acc_sun
    return total_accel, soi_active
