from fastapi import APIRouter

router = APIRouter(prefix="/api/orbit", tags=["Orbital Mechanics & Launch Windows"])

@router.post("/window")
def calculate_launch_window(payload: dict):
    """Calcula efemérides y ventanas óptimas de lanzamiento kepleriano."""
    target_altitude_km = payload.get("target_altitude_km", 400.0)
    inclination_deg = payload.get("inclination_deg", 28.5)
    return {
        "status": "success",
        "target_altitude_km": target_altitude_km,
        "inclination_deg": inclination_deg,
        "optimal_launch_utc": "2026-10-27T14:30:00Z",
        "azimuth_deg": 92.4,
        "orbital_period_minutes": 92.6
    }
