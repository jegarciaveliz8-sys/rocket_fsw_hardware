from fastapi import APIRouter

router = APIRouter(prefix="/api/science", tags=["Scientific Payload & Sensors"])

@router.get("/telemetry")
def get_science_payload_telemetry():
    """Devuelve telemetría en tiempo real de los sensores científicos de a bordo."""
    return {
        "status": "nominal",
        "radiation_sensor": {
            "cpm": 42.5,
            "dose_rate_msv_h": 0.012,
            "status": "ACTIVE"
        },
        "differential_pressure": {
            "pitot_pressure_pa": 10240.5,
            "dynamic_pressure_kpa": 45.2
        },
        "stage_separation": {
            "stage_1_released": True,
            "fairing_jettisoned": True,
            "parachute_status": "STOWED"
        }
    }
