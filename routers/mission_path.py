import math

# Ruta compacta y optimizada alrededor de Sanarate (Radio máximo ~300m)
# Tiempo estimado de circuito completo: ~1.5 a 2 minutos a 12.5 m/s
WAYPOINTS = [
    {"lat": 14.7883, "lon": -90.1988, "alt": 25.0},  # WP 0: Base / Inicio (Despegue)
    {"lat": 14.7900, "lon": -90.1970, "alt": 40.0},  # WP 1: Ascenso y avance al norte (~200m)
    {"lat": 14.7910, "lon": -90.1995, "alt": 50.0},  # WP 2: Desplazamiento oeste dentro de cobertura (~250m)
    {"lat": 14.7870, "lon": -90.2010, "alt": 45.0},  # WP 3: Giro al sur (~300m de la base)
    {"lat": 14.7860, "lon": -90.1980, "alt": 30.0},  # WP 4: Aproximación de retorno
    {"lat": 14.7883, "lon": -90.1988, "alt": 5.0}    # WP 5: RTL / Aterrizaje en Base (Punto A)
]

class MissionNavigator:
    def __init__(self):
        self.current_wp_index = 0
        self.is_active = False

    def start_mission(self):
        self.is_active = True
        self.current_wp_index = 0

    def get_next_position(self, current_lat, current_lon, current_alt):
        if not self.is_active:
            return current_lat, current_lon, current_alt, "STANDBY / READY"

        target = WAYPOINTS[self.current_wp_index]
        
        lat_diff = target["lat"] - current_lat
        lon_diff = target["lon"] - current_lon
        alt_diff = target["alt"] - current_alt
        
        step = 0.08 # Factor de avance por segundo
        
        new_lat = current_lat + (lat_diff * step)
        new_lon = current_lon + (lon_diff * step)
        new_alt = current_alt + (alt_diff * step)

        distance_approx = math.sqrt(lat_diff**2 + lon_diff**2)
        if distance_approx < 0.00015:
            self.current_wp_index += 1
            if self.current_wp_index >= len(WAYPOINTS):
                self.is_active = False
                return target["lat"], target["lon"], target["alt"], "MISSION COMPLETED (RTL)"

        return new_lat, new_lon, new_alt, f"NAVIGATING TO WP {self.current_wp_index + 1}/{len(WAYPOINTS)}"

navigator = MissionNavigator()
