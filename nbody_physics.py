import numpy as np

# Parámetros Gravitacionales Estándar (GM) - IAU / JPL DE440 [m^3/s^2]
MU_EARTH = 3.986004418e14
MU_MOON  = 4.9048695e12
MU_SUN   = 1.32712440018e20

# Constantes astronómicas y de Esferas de Influencia (Laplace & Hill)
R_EARTH_MEAN = 6371008.4
A_MOON_ORBIT = 384400000.0  # Semieje mayor orbital Luna-Tierra
A_EARTH_SUN  = 149597870700.0 # 1 AU

# Radios de Laplace SOI: r_SOI = a * (m / M)^(2/5)
SOI_MOON_LAPLACE = A_MOON_ORBIT * (MU_MOON / MU_EARTH)**0.4  # ~66,183 km
SOI_EARTH_LAPLACE = A_EARTH_SUN * (MU_EARTH / MU_SUN)**0.4  # ~924,675 km

def get_celestial_ephemeris_approx(sim_time_sec: float):
    """
    Calcula los vectores de posición ECI de la Luna y el Sol considerando inclinación 
    y precesión nodal simplificada de orden superior.
    """
    # Luna: Inclinación orbital ~5.14°, velocidad angular media n_moon = 2.6617e-6 rad/s
    n_m = 2.66170726e-6
    i_m = np.radians(5.145)
    
    pos_moon_orbital = np.array([
        A_MOON_ORBIT * np.cos(n_m * sim_time_sec),
        A_MOON_ORBIT * np.sin(n_m * sim_time_sec),
        0.0
    ])
    
    # Matriz de rotación sobre el nodo ascendente (Inclinación i_m)
    R_inc = np.array([
        [1.0, 0.0, 0.0],
        [0.0, np.cos(i_m), -np.sin(i_m)],
        [0.0, np.sin(i_m),  np.cos(i_m)]
    ])
    r_moon_eci = R_inc @ pos_moon_orbital

    # Sol: Velocidad angular orbital media n_sun = 1.990986e-7 rad/s, oblicuidad ε = 23.44°
    n_s = 1.99098659e-7
    e_s = np.radians(23.439291)
    
    pos_sun_ecliptic = np.array([
        A_EARTH_SUN * np.cos(n_s * sim_time_sec),
        A_EARTH_SUN * np.sin(n_s * sim_time_sec),
        0.0
    ])
    
    R_obliquity = np.array([
        [1.0, 0.0, 0.0],
        [0.0, np.cos(e_s), -np.sin(e_s)],
        [0.0, np.sin(e_s),  np.cos(e_s)]
    ])
    r_sun_eci = R_obliquity @ pos_sun_ecliptic
    
    return r_moon_eci, r_sun_eci

def nbody_gravitational_acceleration(pos_eci: np.ndarray, sim_time_sec: float):
    """
    Calcula la aceleración gravitacional vectorial perturbed N-Body 
    (Tierra + Perturbación Lunisolar N-Cuerpos Indirecta).
    
    Aceleración N-Cuerpos respecto al centro de masa terrestre:
    a_i = -GM_i * ( (r - r_i)/||r - r_i||^3 + r_i/||r_i||^3 )
    """
    r_sat = np.linalg.norm(pos_eci)
    if r_sat == 0:
        return np.zeros(3), "EARTH_SOI"
        
    # 1. Aceleración primaria central de la Tierra
    acc_earth = -(MU_EARTH / (r_sat**3)) * pos_eci
    
    # Obtención de Efemérides
    r_moon_eci, r_sun_eci = get_celestial_ephemeris_approx(sim_time_sec)
    
    # 2. Perturbación de la Luna (Ecuación diferencial de 3er cuerpo indirecto)
    r_sat_moon = pos_eci - r_moon_eci
    d_sat_moon = np.linalg.norm(r_sat_moon)
    d_earth_moon = np.linalg.norm(r_moon_eci)
    
    acc_moon_direct = -(MU_MOON / (d_sat_moon**3)) * r_sat_moon
    acc_moon_indirect = -(MU_MOON / (d_earth_moon**3)) * r_moon_eci
    acc_moon_pert = acc_moon_direct - acc_moon_indirect
    
    # 3. Perturbación del Sol (3er cuerpo indirecto)
    r_sat_sun = pos_eci - r_sun_eci
    d_sat_sun = np.linalg.norm(r_sat_sun)
    d_earth_sun = np.linalg.norm(r_sun_eci)
    
    acc_sun_direct = -(MU_SUN / (d_sat_sun**3)) * r_sat_sun
    acc_sun_indirect = -(MU_SUN / (d_earth_sun**3)) * r_sun_eci
    acc_sun_pert = acc_sun_direct - acc_sun_indirect
    
    # Aceleración total perturbada
    total_accel = acc_earth + acc_moon_pert + acc_sun_pert
    
    # Determinación rigurosa de la Esfera de Influencia Activa (Sphere of Influence - SOI)
    if d_sat_moon < SOI_MOON_LAPLACE:
        active_soi = "MOON_LAPLACE_SOI (CISLUNAR_CAPTURE)"
    elif r_sat < SOI_EARTH_LAPLACE:
        active_soi = "EARTH_GEO_LEO_SOI (TERRESTRIAL_DOMINANT)"
    else:
        active_soi = "HELIOCENTRIC_INTERPLANETARY_SOI (MARS_TRANSFER)"
        
    return total_accel, active_soi
