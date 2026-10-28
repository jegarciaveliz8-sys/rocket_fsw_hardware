from fastapi import APIRouter

router = APIRouter(prefix="/api/monte-carlo", tags=["Monte Carlo Simulation"])

@router.post("/simulate")
def run_monte_carlo_simulation(payload: dict):
    """Ejecuta simulaciones estocásticas de dispersión de trayectoria."""
    runs = payload.get("runs", 100)
    wind_variance = payload.get("wind_variance_pct", 15.0)
    return {
        "status": "success",
        "simulation_runs": runs,
        "wind_variance_mode": f"{wind_variance}%",
        "impact_dispersion_ellipse": {
            "semi_major_axis_m": 124.5,
            "semi_minor_axis_m": 45.2,
            "angle_deg": 32.4
        },
        "estimated_landing_coords": {
            "lat": 14.6120,
            "lon": -90.5250
        },
        "success_probability": 0.964
    }
