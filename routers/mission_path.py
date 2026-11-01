import math
import random

class MissionNavigator:
    def __init__(self):
        self.waypoints = [
            {"id": 0, "name": "Base Sanarate", "lat": 14.7883, "lon": -90.1988, "alt": 25.0},
            {"id": 1, "name": "Norte Zona Alta", "lat": 14.7920, "lon": -90.1970, "alt": 40.0},
            {"id": 2, "name": "Desplazamiento Oeste", "lat": 14.7910, "lon": -90.2030, "alt": 50.0},
            {"id": 3, "name": "Giro Sur Perímetro", "lat": 14.7850, "lon": -90.2010, "alt": 45.0},
            {"id": 4, "name": "Aproximación Base", "lat": 14.7865, "lon": -90.1995, "alt": 30.0},
            {"id": 5, "name": "RTL / Aterrizaje", "lat": 14.7883, "lon": -90.1988, "alt": 5.0}
        ]
        self.current_wp_index = 0
        self.is_active = False

    def start_mission(self):
        self.is_active = True
        self.current_wp_index = 0
        return {"status": "SUCCESS", "message": "Misión autónoma iniciada en Sanarate"}

    def abort_mission(self):
        self.is_active = False
        return {"status": "ABORTED", "message": "Misión detenida / RTL forzado"}

    def get_next_position(self, current_lat, current_lon, current_alt):
        if not self.is_active or not self.waypoints:
            return current_lat, current_lon, current_alt, "STANDBY / READY"

        target = self.waypoints[self.current_wp_index]
        
        # Interpolación lineal simple hacia el Waypoint objetivo
        lat_diff = target["lat"] - current_lat
        lon_diff = target["lon"] - current_lon
        alt_diff = target["alt"] - current_alt

        step = 0.00015  # Velocidad de avance en el mapa
        distance = math.sqrt(lat_diff**2 + lon_diff**2)

        if distance < 0.0002:
            # Llegó al waypoint, pasar al siguiente
            status = f"WAYPOINT {self.current_wp_index} ALCANZADO"
            self.current_wp_index += 1
            if self.current_wp_index >= len(self.waypoints):
                self.is_active = False
                return target["lat"], target["lon"], target["alt"], "MISSION COMPLETE (RTL)"
            return target["lat"], target["lon"], target["alt"], status
        else:
            new_lat = current_lat + (lat_diff / distance) * step
            new_lon = current_lon + (lon_diff / distance) * step
            
            # --- SIMULADOR DE VIENTO Y PERTURBACIONES ATMOSFÉRICAS ---
            wind_gust_alt = random.uniform(-0.4, 0.4)
            new_alt = current_alt + (alt_diff * 0.1) + wind_gust_alt
            new_alt = max(2.0, new_alt)
            
            status = f"NAVIGATING TO WP{self.current_wp_index} ({target['name']})"
            return new_lat, new_lon, new_alt, status

navigator = MissionNavigator()
