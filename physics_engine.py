import numpy as np

mu = 3.986004418e14  # Parámetro gravitacional estándar (m^3/s^2)
R_earth = 6378137.0  # Radio ecuatorial de la Tierra (m)
J2 = 1.08262668e-3   # Coeficiente de perturbación J2

def calculate_accelerations(pos, vel, mass, cd, area):
    r = np.linalg.norm(pos)
    if r == 0:
        return np.zeros(3)
        
    x, y, z = pos
    a_grav_central = -mu / (r**3) * pos
    
    factor = (1.5 * J2 * mu * (R_earth**2)) / (r**5)
    z2_r2 = 5.0 * (z**2) / (r**2)
    
    a_j2 = np.array([
        factor * x * (z2_r2 - 1.0),
        factor * y * (z2_r2 - 1.0),
        factor * z * (z2_r2 - 3.0)
    ])
    
    alt = r - R_earth
    rho = 0.0
    if 0 < alt < 1000000:
        rho0 = 1.225
        H = 8500.0
        rho = rho0 * np.exp(-alt / H)
        
    v_norm = np.linalg.norm(vel)
    a_drag = np.zeros(3)
    if rho > 0 and v_norm > 0:
        drag_factor = 0.5 * rho * v_norm * cd * area / mass
        a_drag = -drag_factor * vel
        
    return a_grav_central + a_j2 + a_drag
