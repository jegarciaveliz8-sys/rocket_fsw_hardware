from fastapi import APIRouter

router = APIRouter(prefix="/api/tactical", tags=["HD Tactical & Satellite GIS"])

@router.get("/map-telemetry")
def get_tactical_map_data():
    """Suministra datos geolocalizados en HD para renderizado en mapa satelital."""
    return {
        "map_provider": "ESRI_MAPBOX_SATELLITE_HD",
        "projection": "EPSG:4326",
        "bounds": {
            "lat_min": 14.0, "lat_max": 15.0,
            "lon_min": -91.0, "lon_max": -90.0
        },
        "current_position": {
            "lat": 14.5975, "lon": -90.5131, "alt_m": 21974.7,
            "heading": 182.4, "ground_speed_knots": 420.5
        },
        "ground_track_history": [
            {"lat": 14.5000, "lon": -90.5000, "alt": 5000.0},
            {"lat": 14.5500, "lon": -90.5100, "alt": 12000.0},
            {"lat": 14.5975, "lon": -90.5131, "alt": 21974.7}
        ],
        "geofence_zones": [
            {
                "id": "RESTRICTED_AIRSPACE_ALPHA",
                "risk_level": "HIGH",
                "polygon": [[14.7, -90.8], [14.7, -90.3], [14.3, -90.3], [14.3, -90.8]]
            }
        ]
    }
