from fastapi import APIRouter
from fastapi.responses import Response

router = APIRouter(prefix="/api/reports", tags=["Reports & Vectors"])

@router.get("/pdf", response_class=Response)
def generate_mission_pdf_report():
    """Genera y descarga un reporte consolidado de la misión en formato PDF."""
    pdf_dummy_bytes = b"%PDF-1.4 ODYSSEY-1 MISSION REPORT - NOMINAL FLIGHT SUMMARY"
    return Response(
        content=pdf_dummy_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=odyssey_mission_report.pdf"}
    )

@router.get("/vectors")
def get_flight_vectors():
    """Calcula y devuelve vectores de trayectoria y velocidad actual (EKF)."""
    return {
        "status": "success",
        "position_vector": [14.5975, -90.5131, 21974.7],
        "velocity_vector": [120.5, 45.2, 777.74],
        "acceleration_vector": [0.05, 0.01, 9.81],
        "heading_degrees": 182.4
    }
