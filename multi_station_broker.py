import asyncio
import time
import random
from typing import Dict, Any, List

class MultiStationBroker:
    def __init__(self):
        # Estaciones DSN soportadas por el sistema
        self.stations: Dict[str, Dict[str, Any]] = {
            "DSS-63": {"name": "Madrid (DSS-63)", "status": "ACTIVE", "frequency": "8.42 GHz", "snr": 18.4},
            "DSS-14": {"name": "Goldstone (DSS-14)", "status": "STANDBY", "frequency": "8.45 GHz", "snr": 16.2},
            "DSS-43": {"name": "Canberra (DSS-43)", "status": "STANDBY", "frequency": "8.41 GHz", "snr": 14.9}
        }
        self.active_station = "DSS-63"

    def set_active_station(self, station_id: str) -> bool:
        """Conmuta la estación terrena activa para el enlace FSW."""
        if station_id in self.stations:
            for s_id in self.stations:
                self.stations[s_id]["status"] = "STANDBY"
            self.stations[station_id]["status"] = "ACTIVE"
            self.active_station = station_id
            return True
        return False

    def get_station_telemetry(self) -> Dict[str, Any]:
        """Genera telemetría adaptada a las condiciones de la estación activa."""
        t = time.time()
        active_info = self.stations[self.active_station]
        
        # Variación de SNR según la estación activa simulada
        snr_jitter = random.uniform(-0.4, 0.4)
        current_snr = round(active_info["snr"] + snr_jitter, 1)

        return {
            "time": int(t % 86400),
            "timestamp": time.strftime("%H:%M:%S"),
            "altitude": round(398.0 + random.uniform(-2.0, 2.0), 2),
            "velocity": round(7668.0 + random.uniform(-10.0, 10.0), 2),
            "chamber_pressure": round(15.4 + random.uniform(-0.3, 0.3), 1),
            "battery_pct": round(max(20.0, 94.5 - (t % 300) * 0.05), 1),
            "status": f"LOCKED ({self.active_station})",
            "pitch": round(3.92 + random.uniform(-0.5, 0.5), 2),
            "roll": round(161.0 + random.uniform(-2.0, 2.0), 1),
            "yaw": round(random.uniform(-1.0, 1.0), 2),
            "ccsds_frame": f"01AF{hex(int(t))[2:].upper()}414C543A3339382E38352FDC",
            "active_station": active_info["name"],
            "snr": current_snr,
            "stations_status": self.stations,
            "alerts": []
        }

broker = MultiStationBroker()
