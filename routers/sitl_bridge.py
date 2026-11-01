from pymavlink import mavutil

class SITLBridge:
    def __init__(self, connection_string='udp:127.0.0.1:14550'):
        self.connection_string = connection_string
        self.master = None

    def connect(self):
        try:
            self.master = mavutil.mavlink_connection(self.connection_string)
            print(f"🔗 [SITL BRIDGE] Conectado a ArduPilot en {self.connection_string}")
        except Exception as e:
            print(f"⚠️ [SITL BRIDGE] No se pudo conectar: {e}")

    def get_telemetry_packet(self):
        if not self.master:
            return None
        msg = self.master.recv_match(type='GLOBAL_POSITION_INT', blocking=False)
        if msg:
            return {
                "lat": msg.lat / 1e7,
                "lon": msg.lon / 1e7,
                "altitude": msg.relative_alt / 1000.0,
                "velocity": msg.vx / 100.0
            }
        return None

sitl_client = SITLBridge()
