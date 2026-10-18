import os
from celery import Celery

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "rocket_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL
)

@celery_app.task(name="process_post_flight_report")
def process_post_flight_report(mission_duration: int, max_altitude: float):
    # Simulación de un procesamiento pesado en segundo plano
    print(f"[CELERY] Generando reporte analítico para misión de {mission_duration}s (Altitud máx: {max_altitude}km)...")
    return {"status": "SUCCESS", "report_id": 9942, "max_altitude": max_altitude}
