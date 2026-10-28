from fastapi import APIRouter

router = APIRouter(prefix="/api/network-sim", tags=["Network Resilience"])

@router.post("/impairment")
def configure_network_impairment(payload: dict):
    """Simula degradación de enlace (latencia, jitter, pérdida de paquetes)."""
    latency_ms = payload.get("latency_ms", 50)
    packet_loss_pct = payload.get("packet_loss_pct", 1.0)
    return {
        "status": "success",
        "simulated_latency_ms": latency_ms,
        "simulated_packet_loss_pct": packet_loss_pct,
        "link_state": "DEGRADED" if packet_loss_pct > 5.0 else "NOMINAL"
    }
