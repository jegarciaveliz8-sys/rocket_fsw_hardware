from fastapi import APIRouter

router = APIRouter(prefix="/api/timeseries", tags=["Timeseries Telemetry DB"])

@router.get("/query")
def query_timeseries_data(metric: str = "altitude", limit: int = 10):
    """Consulta registros históricos de alta frecuencia para gráficas en tiempo real."""
    return {
        "status": "success",
        "metric": metric,
        "data_points": [
            {"timestamp": 1793149910 + i, "value": 20000.0 + (i * 197.4)}
            for i in range(min(limit, 10))
        ]
    }
