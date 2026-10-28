from fastapi import APIRouter

router = APIRouter(prefix="/api/weather", tags=["Meteorology & Wind Profiles"])

@router.get("/profile")
def get_altitude_wind_profile():
    """Suministra perfiles atmosféricos y de cizalladura de viento en altura."""
    return {
        "status": "success",
        "station": "PAD_ALPHA_MET",
        "surface_wind_knots": 8.5,
        "wind_direction_deg": 180,
        "wind_shear_detected": False,
        "altitude_wind_layers": [
            {"alt_m": 1000, "speed_knots": 12.0, "dir_deg": 185},
            {"alt_m": 5000, "speed_knots": 35.4, "dir_deg": 210},
            {"alt_m": 12000, "speed_knots": 65.2, "dir_deg": 240}
        ]
    }
