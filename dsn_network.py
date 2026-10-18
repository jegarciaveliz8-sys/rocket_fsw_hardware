import numpy as np

# Coordenadas geodésicas de estaciones DSN [Latitud (°), Longitud (°), Altitud (m)]
DSN_STATIONS = {
    "Cape Canaveral (USA)": {"lat": 28.3922, "lon": -80.6077, "alt": 3.0},
    "Madrid (Spain)": {"lat": 40.4295, "lon": -4.2497, "alt": 834.0},
    "Goldstone (USA)": {"lat": 35.3390, "lon": -116.8750, "alt": 1016.0},
    "Canberra (Australia)": {"lat": -35.4014, "lon": 148.9819, "alt": 662.0}
}

def calculate_active_dsn_station(pos_eci, sim_time_seconds):
    """
    Calcula la rotación terrestre y determina qué estación DSN tiene línea de visión directa (Elevation > 10°).
    """
    # Rotación de la Tierra en función del tiempo (WGS84 Earth rotation rate ~ 7.292115e-5 rad/s)
    omega_earth = 7.292115e-5
    theta = omega_earth * sim_time_seconds
    
    # Matriz de rotación ECI a ECEF simplificada alrededor del eje Z
    cos_t = np.cos(theta)
    sin_t = np.sin(theta)
    
    x, y, z = pos_eci
    x_ecef = cos_t * x + sin_t * y
    y_ecef = -sin_t * x + cos_t * y
    z_ecef = z
    
    r_ecef = np.array([x_ecef, y_ecef, z_ecef])
    
    best_station = "Cape Canaveral (USA)"
    max_elevation = -90.0
    
    for name, coords in DSN_STATIONS.items():
        lat_rad = np.radians(coords["lat"])
        lon_rad = np.radians(coords["lon"])
        
        # Posición aproximada de la estación en ECEF
        R_e = 6378137.0 + coords["alt"]
        station_ecef = np.array([
            R_e * np.cos(lat_rad) * np.cos(lon_rad),
            R_e * np.cos(lat_rad) * np.sin(lon_rad),
            R_e * np.sin(lat_rad)
        ])
        
        # Vector cenital / elevación aproximada por producto escalar normalizado
        vector_to_sat = r_ecef - station_ecef
        dist = np.linalg.norm(vector_to_sat)
        if dist == 0:
            continue
            
        unit_sat = vector_to_sat / dist
        unit_station = station_ecef / np.linalg.norm(station_ecef)
        
        elevation_angle = 90.0 - np.degrees(np.arccos(np.clip(np.dot(unit_sat, unit_station), -1.0, 1.0)))
        
        if elevation_angle > max_elevation:
            max_elevation = elevation_angle
            best_station = name
            
    return best_station, round(max_elevation, 1)
