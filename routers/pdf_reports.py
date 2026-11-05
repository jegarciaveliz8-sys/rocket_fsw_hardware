import sqlite3
import io
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

router = APIRouter(prefix="/api/audit", tags=["PDF Reports"])

@router.get("/export/pdf")
def generate_pdf_audit_report():
    conn = sqlite3.connect("odyssey_telemetry.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*), MAX(altitude), MAX(velocity) FROM flight_logs")
    total_frames, max_alt, max_vel = cursor.fetchone()
    
    cursor.execute("SELECT COUNT(*) FROM flight_logs WHERE status LIKE '%ALERT%' OR status LIKE '%BREACH%'")
    total_anomalies = cursor.fetchone()[0]
    conn.close()

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle("ODYSSEY-1 Post-Flight Audit Report")

    # Cabecera del documento
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, 750, "ODYSSEY-1 // Reporte de Auditoría Post-Vuelo (HIL)")
    
    pdf.setFont("Helvetica", 11)
    pdf.drawString(50, 725, "Estación Terrena Sanarate, Guatemala")
    pdf.line(50, 715, 560, 715)

    # Cuerpo y métricas clave
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, 680, "Resumen de la Misión:")
    
    pdf.setFont("Helvetica", 10)
    pdf.drawString(70, 655, f"• Total de tramas de telemetría analizadas: {total_frames}")
    pdf.drawString(70, 635, f"• Altitud máxima registrada: {max_alt or 0.0} metros")
    pdf.drawString(70, 615, f"• Velocidad máxima registrada: {max_vel or 0.0} m/s")
    pdf.drawString(70, 595, f"• Alertas FDIR / Anomalías críticas detectadas: {total_anomalies}")

    pdf.setFont("Helvetica-Oblique", 9)
    pdf.drawString(50, 100, "Documento generado automáticamente por el sistema ODYSSEY-1 GCS.")

    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=odyssey_mission_audit.pdf"}
    )
