import numpy as np

# Constantes WGS84 / IAU
MU = 3.986004418e14        # m^3/s^2
R_EARTH = 6378137.0        # m
J2 = 1.08262668e-3
J3 = -2.53241052e-6
J4 = -1.61992164e-6
P_SUN = 4.56e-6            # Presión de radiación solar N/m^2 a 1 AU

def get_atmospheric_density(alt_m):
    """Modelo atmosférico por capas US Standard Atmosphere 1976 simplificado"""
    if alt_m < 0:
        return 1.225
    elif alt_m < 11000:
        T = 288.15 - 0.0065 * alt_m
        p = 101325 * (T / 288.15) ** 5.25588
        return p / (287.05 * T)
    elif alt_m < 25000:
        T = 216.65
        p = 22632.1 * np.exp(-9.80665 * 0.0289644 * (alt_m - 11000) / (8.31432 * T))
        return p / (287.05 * T)
    elif alt_m < 50000:
        T = 216.65 + 0.001 * (alt_m - 25000)
        p = 2488.72 * (T / 216.65) ** -34.16319
        return p / (287.05 * T)
    elif alt_m < 100000:
        # Mesosfera alta
        return 1.225 * np.exp(-alt_m / 7400.0)
    elif alt_m < 600000:
        # Termosfera / Arrastre LEO
        return 1.225 * np.exp(-alt_m / 50000.0)
    else:
        return 0.0

def state_derivative(t, state, mass, cd, area, cr=1.2):
    """
    Calcula dState/dt = [vx, vy, vz, ax, ay, az]
    state: [x, y, z, vx, vy, vz]
    """
    pos = state[:3]
    vel = state[3:]
    r = np.linalg.norm(pos)
    if r == 0:
        return np.zeros(6)
        
    x, y, z = pos
    z2 = z**2
    r2 = r**2
    
    # 1. Aceleración Gravitacional Central
    a_central = -MU / (r**3) * pos
    
    # 2. Perturbaciones armónicas J2, J3, J4 (Ecuaciones ECI)
    # J2
    f_j2 = (1.5 * J2 * MU * R_EARTH**2) / (r**5)
    a_j2 = np.array([
        f_j2 * x * (5.0 * z2 / r2 - 1.0),
        f_j2 * y * (5.0 * z2 / r2 - 1.0),
        f_j2 * z * (5.0 * z2 / r2 - 3.0)
    ])
    
    # J3
    f_j3 = (0.5 * J3 * MU * R_EARTH**3) / (r**7)
    a_j3 = np.array([
        f_j3 * x * z * (35.0 * z2 / r2 - 15.0),
        f_j3 * y * z * (35.0 * z2 / r2 - 15.0),
        f_j3 * (35.0 * (z**4) / (r2**2) - 30.0 * z2 / r2 + 3.0)
    ])
    
    # 3. Arrastre Atmosférico Aerodinámico
    alt = r - R_EARTH
    rho = get_atmospheric_density(alt)
    v_norm = np.linalg.norm(vel)
    a_drag = np.zeros(3)
    if rho > 0 and v_norm > 0:
        a_drag = -0.5 * rho * (v_norm) * cd * (area / mass) * vel
        
    # 4. Presión de Radiación Solar (SRP)
    # Asumiendo vector Sol apuntando en +X en ECI para simulación
    a_srp = -(P_SUN * cr * area / mass) * np.array([1.0, 0.0, 0.0]) if alt > 100000 else np.zeros(3)
    
    a_total = a_central + a_j2 + a_j3 + a_drag + a_srp
    return np.hstack([vel, a_total])

def rk4_step(state, dt, mass, cd, area):
    """Integrador de Runge-Kutta de 4º Orden"""
    k1 = state_derivative(0, state, mass, cd, area)
    k2 = state_derivative(0, state + 0.5 * dt * k1, mass, cd, area)
    k3 = state_derivative(0, state + 0.5 * dt * k2, mass, cd, area)
    k4 = state_derivative(0, state + dt * k3, mass, cd, area)
    return state + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
