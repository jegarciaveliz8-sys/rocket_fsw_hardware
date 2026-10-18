import numpy as np
import physics_engine

class SwarmConstellationManager:
    """
    Gestor de constelación multi-satélite basado en marco orbital local LVLH (Hill-Clohessy-Wiltshire).
    """
    def __init__(self):
        self.fleet = {
            "ODYSSEY-LEO-1": {
                "state": np.array([6778137.0, 0.0, 0.0, 0.0, 7670.0, 0.0]),
                "mass": 50000.0, "cd": 0.3, "area": 10.0
            },
            "ODYSSEY-LEO-2": {
                "state": np.array([6788137.0, 5000.0, 0.0, 0.0, 7665.0, 0.0]),
                "mass": 8500.0, "cd": 0.22, "area": 3.2
            }
        }

    def propagate_swarm_fleet(self, dt=1.0):
        telemetry_aggregate = {}
        
        for name, data in self.fleet.items():
            # Propagación numérica RK4 de alta fidelidad individual
            new_state = physics_engine.rk4_step(data["state"], dt, data["mass"], data["cd"], data["area"])
            self.fleet[name]["state"] = new_state
            
            pos = new_state[:3]
            vel = new_state[3:]
            alt = np.linalg.norm(pos) - 6378137.0
            
            telemetry_aggregate[name] = {
                "position_xyz": [round(float(p), 2) for p in pos],
                "altitude_km": round(alt / 1000.0, 3),
                "speed_ms": round(float(np.linalg.norm(vel)), 2)
            }
            
        # Análisis de Proximidad Relativa (Distancia euclidiana entre vehículos de la flota)
        pos_1 = self.fleet["ODYSSEY-LEO-1"]["state"][:3]
        pos_2 = self.fleet["ODYSSEY-LEO-2"]["state"][:3]
        relative_distance_m = float(np.linalg.norm(pos_1 - pos_2))
        
        telemetry_aggregate["CONSTELLATION_METRICS"] = {
            "relative_distance_m": round(relative_distance_m, 2),
            "collision_risk_flag": relative_distance_m < 1000.0  # Alerta si están a menos de 1 km
        }
        
        return telemetry_aggregate
