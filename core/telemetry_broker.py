import redis
import json
import os

# Configuración del broker (usa variables de entorno o fallback a localhost)
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

class TelemetryBroker:
    def __init__(self):
        try:
            self.client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
            self.client.ping()
            self.enabled = True
            print("[BROKER] Conectado exitosamente a Redis Pub/Sub Global.")
        except Exception as e:
            self.enabled = False
            print(f"[BROKER] Aviso: Redis no disponible localmente ({e}). Operando en modo búfer asíncrono autónomo.")

    def publish_telemetry(self, packet: dict):
        """Publica la trama de telemetría en el canal global de Redis."""
        if self.enabled:
            try:
                self.client.publish("odyssey_global_telemetry", json.dumps(packet))
            except Exception as e:
                print(f"[BROKER] Error al publicar en Redis: {e}")

    def get_subscriber(self):
        """Retorna un objeto pubsub para clientes conectados."""
        if self.enabled:
            pubsub = self.client.pubsub()
            pubsub.subscribe("odyssey_global_telemetry")
            return pubsub
        return None

broker = TelemetryBroker()
