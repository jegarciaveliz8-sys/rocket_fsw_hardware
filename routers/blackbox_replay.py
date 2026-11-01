from fastapi import APIRouter
import os
import csv

router = APIRouter(prefix="/api/replay", tags=["Flight Replay"])

@router.get("/load/{filename}")
async def load_flight_log(filename: str):
    filepath = os.path.join("blackbox_logs", filename)
    if not os.path.exists(filepath):
        return {"status": "ERROR", "message": "Archivo de caja negra no encontrado"}
    
    packets = []
    with open(filepath, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            packets.append(row)
    
    return {"status": "SUCCESS", "total_frames": len(packets), "data": packets}
