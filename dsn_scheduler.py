import numpy as np

MU_EARTH = 3.986004418e14
R_EARTH = 6378137.0

# Coordenadas ECEF / Geodésicas de Estaciones DSN
STATIONS = {
    "DSN_MADRID": {"lat": 40.427, "lon": -4.248, "min_elevation_deg": 10.0},
    "DSN_GOLDSTONE": {"lat": 35.426, "lon": -116.890, "min_elevation_deg": 10.0},
    "DSN_CANBERRA": {"lat": -35.401, "lon": 148.981, "min_elevation_deg": 10.0}
}

def predict_dsn_passes(r_eci: np.ndarray, v_eci: np.ndarray, horizon_seconds: int = 5400, step_sec: int = 60):
    """
    Predice las ventanas de visibilidad (AOS / LOS) propagando el estado orbital
    durante un horizonte de tiempo determinado.
    """
    omega_earth = 7.2921159e-5  # rad/s
    pass_schedule = []
    
    current_r = np.copy(r_eci)
    current_v = np.copy(v_eci)
    
    for t in range(0, horizon_seconds, step_sec):
        # Propagación кеpleriana rápida para predicción
        r_mag = np.linalg.norm(current_r)
        a_grav = - (MU_EARTH / (r_mag**3)) * current_r
        current_v += a_grav * step_sec
        current_r += current_v * step_sec
        
        # Rotación ECI a ECEF
        theta_gst = omega_earth * t
        R_z = np.array([
            [np.cos(theta_gst), np.sin(theta_gst), 0],
            [-np.sin(theta_gst), np.cos(theta_gst), 0],
            [0, 0, 1]
        ])
        r_ecef = R_z @ current_r
        
        # Evaluar visibilidad para cada estación
        for name, info in STATIONS.items():
            lat_rad = np.radians(info["lat"])
            lon_rad = np.radians(info["lon"])
            
            r_st = (R_EARTH) * np.array([
                np.cos(lat_rad) * np.cos(lon_rad),
                np.cos(lat_rad) * np.sin(lon_rad),
                np.sin(lat_rad)
            ])
            
            rho = r_ecef - r_st
            rho_mag = np.linalg.norm(rho)
            up = r_st / R_EARTH
            sin_elev = np.dot(rho, up) / rho_mag
            elevation_deg = np.degrees(np.arcsin(np.clip(sin_elev, -1.0, 1.0)))
            
            if elevation_deg >= info["min_elevation_deg"]:
                pass_schedule.append({
                    "time_offset_sec": t,
                    "station": name,
                    "elevation_deg": round(float(elevation_deg), 2),
                    "range_km": round(float(rho_mag / 1000.0), 2)
                })
                break  # Tomar la estación con mejor o primera cobertura
                
    return pass_schedule[:10]  # Retornar los primeros 10 eventos
