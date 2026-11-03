from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/dsn", tags=["DSN Global Network"])

# Catálogo oficial de estaciones de rastreo mundial (Deep Space Network)
DSN_STATIONS = {
    "sanarate": {
        "id": "sanarate",
        "name": "Sanarate Ground Station [HIL]",
        "lat": 14.7883,
        "lon": -90.1988,
        "country": "Guatemala",
        "type": "HIL Tactical Hub"
    },
    "madrid": {
        "id": "madrid",
        "name": "Madrid Deep Space Communications (DSS-63)",
        "lat": 40.4318,
        "lon": -4.2486,
        "country": "Spain",
        "type": "Deep Space Node"
    },
    "goldstone": {
        "id": "goldstone",
        "name": "Goldstone Deep Space Complex (DSS-13)",
        "lat": 35.4266,
        "lon": -116.8895,
        "country": "USA",
        "type": "Deep Space Node"
    },
    "canberra": {
        "id": "canberra",
        "name": "Canberra Deep Space Complex (DSS-34)",
        "lat": -35.4014,
        "lon": 148.9816,
        "country": "Australia",
        "type": "Deep Space Node"
    }
}

# Estación activa por defecto (Sanarate HIL)
active_dsn = DSN_STATIONS["sanarate"]

class StationSelection(BaseModel):
    station_id: str

@router.get("/stations")
def get_dsn_stations():
    """Retorna el catálogo global de estaciones y la estación activa actual."""
    return {
        "active_station": active_dsn,
        "available_stations": DSN_STATIONS
    }

@router.post("/set_station")
def set_active_station(payload: StationSelection):
    """Cambia dinámicamente la estación terrena base de la misión a nivel mundial."""
    global active_dsn
    if payload.station_id in DSN_STATIONS:
        active_dsn = DSN_STATIONS[payload.station_id]
        return {
            "status": "success",
            "message": f"Estación DSN cambiada a {active_dsn['name']}",
            "active_station": active_dsn
        }
    return {"status": "error", "message": "Estación DSN no encontrada en el registro global."}, 404
