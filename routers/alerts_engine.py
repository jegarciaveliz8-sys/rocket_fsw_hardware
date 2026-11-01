import math

_last_alert_states = {}

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
    global _last_alert_states
    alerts = []
    
    altitude = telemetry_data.get("altitude", 0)
    velocity = telemetry_data.get("velocity", 0)
    chamber_pressure = telemetry_data.get("chamber_pressure", 15.4)
    battery_pct = telemetry_data.get("battery_pct", 100.0)
    lat = telemetry_data.get("lat", BASE_LAT)
    lon = telemetry_data.get("lon", BASE_LON)
    
    current_conditions = {}
    
    # 1. Validación de Geocerca (Sanarate Perimetro)
    distance_from_base = calculate_distance(BASE_LAT, BASE_LON, lat, lon)
    if distance_from_base > MAX_ALLOWED_RADIUS_METERS:
        current_conditions["GEOFENCE_BREACH"] = {
            "level": "CRITICAL",
            "message": f"¡VIOLACIÓN DE GEOCERCA! Dron a {distance_from_base:.1f}m del punto base."
        }
    
    # 2. Regla de Altitud
    if altitude > 120.0: # Límite legal estándar para drones recreativos/comerciales
        current_conditions["ALTITUDE_WARNING"] = {
            "level": "WARNING",
            "message": f"Límite de altitud FAA/DGAC alcanzado: {altitude}m"
        }
        
    # 3. Regla de Velocidad
    if velocity > 15.0:
        current_conditions["VELOCITY_CRITICAL"] = {
            "level": "CRITICAL",
            "message": f"Exceso de velocidad crítico: {velocity} m/s"
        }

    # 4. Presión de Cámara (Pc)
    if chamber_pressure > 18.0:
        current_conditions["PRESSURE_HIGH"] = {
            "level": "CRITICAL",
            "message": f"¡Sobrepresión crítica en cámara! Pc: {chamber_pressure} MPa"
        }
    elif chamber_pressure < 12.0:
        current_conditions["PRESSURE_LOW"] = {
            "level": "WARNING",
            "message": f"Caída de presión en cámara (Pc baja): {chamber_pressure} MPa"
        }

    # 5. Batería
    if battery_pct < 20.0:
        lvl = "CRITICAL" if battery_pct < 10.0 else "WARNING"
        current_conditions["BATTERY_LOW"] = {
            "level": lvl,
            "message": f"Nivel de batería bajo: {battery_pct}%"
        }
        
    # 6. Integridad CRC
    if not telemetry_data.get("crc_valid", True):
        current_conditions["CRC_ERROR"] = {
            "level": "CRITICAL",
            "message": "Pérdida de integridad en paquetes CCSDS / CRC Inválido"
        }

    # Filtrar para enviar solo nuevas alertas o cambios de estado
    for key, alert_data in current_conditions.items():
        if key not in _last_alert_states or _last_alert_states[key] != alert_data["message"]:
            alerts.append(alert_data)
            _last_alert_states[key] = alert_data["message"]
            
    resolved_keys = [k for k in _last_alert_states if k not in current_conditions]
    for k in resolved_keys:
        del _last_alert_states[k]
        
    return alerts
