import math
from routers import fault_injection

# Coordenadas base de referencia en Sanarate (Punto de lanzamiento)
BASE_LAT = 14.7883
BASE_LON = -90.1988
MAX_ALLOWED_RADIUS_METERS = 500.0  # Límite de la geocerca: 500 metros

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calcula la distancia aproximada en metros entre dos coordenadas GPS (Haversine simplificado)."""
    R = 6371000  # Radio de la Tierra en metros
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def check_telemetry_alerts(telemetry_data: dict) -> list:
    alerts = []
    
    altitude = telemetry_data.get("altitude", 0)
    velocity = telemetry_data.get("velocity", 0)
    chamber_pressure = telemetry_data.get("chamber_pressure", 15.4)
    battery_pct = telemetry_data.get("battery_pct", 100.0)
    lat = telemetry_data.get("lat", BASE_LAT)
    lon = telemetry_data.get("lon", BASE_LON)
    
    # 1. Validación de Inyección de Fallos FDIR (Prioridad alta)
    if fault_injection.fault_state.get("rf_blackout"):
        alerts.append({
            "level": "CRITICAL",
            "message": "⚠️ FDIR: Pérdida total de enlace RF (Blackout DSN simulado)"
        })
        
    if fault_injection.fault_state.get("gps_failure"):
        alerts.append({
            "level": "WARNING",
            "message": "🛰️ FDIR: Falla de GPS (No Fix / IMU Dead Reckoning activo)"
        })
        
    if fault_injection.fault_state.get("low_battery_spike"):
        alerts.append({
            "level": "CRITICAL",
            "message": "⚡ FDIR: Pico crítico de descarga en banco de baterías"
        })

    # 2. Validación de Geocerca (Sanarate Perimetro)
    distance_from_base = calculate_distance(BASE_LAT, BASE_LON, lat, lon)
    if distance_from_base > MAX_ALLOWED_RADIUS_METERS:
        alerts.append({
            "level": "CRITICAL",
            "message": f"¡VIOLACIÓN DE GEOCERCA! Dron a {distance_from_base:.1f}m del punto base."
        })
    
    # 3. Regla de Altitud
    if altitude > 120.0:
        alerts.append({
            "level": "WARNING",
            "message": f"Límite de altitud FAA/DGAC alcanzado: {altitude}m"
        })
        
    # 4. Regla de Velocidad
    if velocity > 15.0:
        alerts.append({
            "level": "CRITICAL",
            "message": f"Exceso de velocidad crítico: {velocity} m/s"
        })

    # 5. Presión de Cámara (Pc)
    if chamber_pressure > 18.0:
        alerts.append({
            "level": "CRITICAL",
            "message": f"¡Sobrepresión crítica en cámara! Pc: {chamber_pressure} MPa"
        })
    elif chamber_pressure < 12.0:
        alerts.append({
            "level": "WARNING",
            "message": f"Caída de presión en cámara (Pc baja): {chamber_pressure} MPa"
        })

    # 6. Batería normal
    if battery_pct < 20.0 and not fault_injection.fault_state.get("low_battery_spike"):
        lvl = "CRITICAL" if battery_pct < 10.0 else "WARNING"
        alerts.append({
            "level": lvl,
            "message": f"Nivel de batería bajo: {battery_pct}%"
        })
        
    # 7. Integridad CRC
    if not telemetry_data.get("crc_valid", True):
        alerts.append({
            "level": "CRITICAL",
            "message": "Pérdida de integridad en paquetes CCSDS / CRC Inválido"
        })
        
    return alerts
