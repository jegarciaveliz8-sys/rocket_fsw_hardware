import math
import time
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/mission", tags=["Mission Path"])

class TargetClickRequest(BaseModel):
    lat: float
    lon: float

class MissionNavigator:
    def __init__(self):
        self.waypoints = []
        self.current_wp_index = 0
        self.is_active = False
        self.loiter_timer = 0
        self.loiter_duration = 0
        self.action_triggered = False
        self.base_coords = {"lat": 14.7883, "lon": -90.1988, "alt": 0.0}

    def load_waypoints(self, waypoints):
        self.waypoints = waypoints
        self.current_wp_index = 0
        self.is_active = True
        self.loiter_timer = 0
        self.action_triggered = False

    def set_dynamic_target(self, lat: float, lon: float):
        dynamic_waypoint = [{"lat": lat, "lon": lon, "alt": 50.0, "loiter": 3}]
        self.load_waypoints(dynamic_waypoint)
        return {"status": "SUCCESS", "target": {"lat": lat, "lon": lon}}

    def update_position(self, current_state):
        if not self.is_active or not self.waypoints:
            return current_state

        # Si ya terminamos todos los waypoints, activar RTL automático a la base
        if self.current_wp_index >= len(self.waypoints):
            return self.execute_rtl(current_state)

        target = self.waypoints[self.current_wp_index]
        target_lat = target.get("lat", 14.7883)
        target_lon = target.get("lon", -90.1988)
        target_alt = target.get("alt", 35.0)
        loiter_time = target.get("loiter", 0) # Segundos de espera

        curr_lat = current_state["lat"]
        curr_lon = current_state["lon"]

        # Calcular distancia aproximada al waypoint actual
        lat_diff = target_lat - curr_lat
        lon_diff = target_lon - curr_lon
        distance = math.sqrt(lat_diff**2 + lon_diff**2)

        # Umbral de llegada (aproximadamente 5-10 metros)
        if distance < 0.00015:
            # Llegó al waypoint
            if loiter_time > 0:
                if self.loiter_timer == 0:
                    self.loiter_timer = time.time()
                    current_state.setdefault("alerts", []).append(f"Llegando a WP{self.current_wp_index}. Iniciando Loiter ({loiter_time}s) y ráfaga fotográfica 📸")
                
                elapsed = time.time() - self.loiter_timer
                current_state["velocity"] = 0.0 # Estacionario en Loiter
                
                if elapsed >= loiter_time:
                    # Termino el Loiter, pasar al siguiente punto
                    self.loiter_timer = 0
                    self.current_wp_index += 1
            else:
                # Sin loiter, disparo rápido y avanzar
                current_state.setdefault("alerts", []).append(f"WP{self.current_wp_index} alcanzado. 📸 Foto capturada.")
                self.current_wp_index += 1
        else:
            # Tránsito hacia el waypoint (interpolación suave)
            speed = 0.00008 # Velocidad de avance vectorial
            current_state["lat"] += (lat_diff / distance) * speed
            current_state["lon"] += (lon_diff / distance) * speed
            current_state["altitude"] = target_alt
            current_state["velocity"] = 12.5

        return current_state

    def execute_rtl(self, current_state):
        # Modo Return to Launch hacia la base de Sanarate
        lat_diff = self.base_coords["lat"] - current_state["lat"]
        lon_diff = self.base_coords["lon"] - current_state["lon"]
        distance = math.sqrt(lat_diff**2 + lon_diff**2)

        if distance < 0.00015:
            current_state["lat"] = self.base_coords["lat"]
            current_state["lon"] = self.base_coords["lon"]
            current_state["altitude"] = 0.0
            current_state["velocity"] = 0.0
            current_state["status"] = "MISSION COMPLETE / LANDED"
            self.is_active = False
            current_state.setdefault("alerts", []).append("RTL completado con éxito. Aterrizaje en Base Sanarate.")
        else:
            speed = 0.0001
            current_state["lat"] += (lat_diff / distance) * speed
            current_state["lon"] += (lon_diff / distance) * speed
            current_state["altitude"] = 25.0
            current_state["velocity"] = 15.0
            current_state["status"] = "RTL (RETURNING TO LAUNCH)"

        return current_state

navigator = MissionNavigator()

@router.post("/set_click_target")
def set_click_target(req: TargetClickRequest):
    return navigator.set_dynamic_target(req.lat, req.lon)
