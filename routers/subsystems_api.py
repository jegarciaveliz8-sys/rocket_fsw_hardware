import json
from fastapi import APIRouter, Response

router = APIRouter()

# Estado en memoria para persistir la conmutación interactiva de las subestaciones desde la UI
SUBSTATION_STATES = {
    "SUB-01": {"status": "NOMINAL", "load_pct": 68.5},
    "SUB-02": {"status": "NOMINAL", "load_pct": 42.1},
    "SUB-03": {"status": "NOMINAL", "load_pct": 89.2}
}

# Configuración en memoria para el propagador orbital interactivo
ORBITAL_CONFIG = {
    "gravity_model": "J2_J4",
    "dsn_station": "Madrid (DSS-63)"
}

@router.post("/api/mission/abort")
def mission_abort():
    return {"status": "ABORT_SEQUENCE_ACTIVATED", "message": "Abort sequence activated successfully"}

@router.get("/api/logs/export")
def export_logs():
    return {"logs": ["[T+0s] System initialized"]}

@router.get("/export/csv")
def export_csv():
    return {"export": "success", "format": "csv", "error": "No active telemetry records to export"}

@router.post("/ai/query")
@router.post("/api/ai/query")
def ai_query(data: dict):
    return {"response": "Telemetry nominal."}

@router.post("/api/dvr/start")
def dvr_start():
    return {"dvr": "started", "dvr_state": "RECORDING", "recording": True}

@router.post("/api/dvr/stop")
def dvr_stop():
    return {"dvr": "stopped", "dvr_state": "STOPPED", "recording": False, "status": "success"}

@router.get("/api/dvr/sessions")
def dvr_sessions():
    return {"sessions": [{"id": 1, "filename": "session_001.mp4"}]}

@router.get("/api/reports/pdf")
def pdf_report():
    return Response(content=b"%PDF-1.4 mock pdf content", media_type="application/pdf")

@router.get("/api/reports/vectors")
def flight_vectors():
    return {
        "vectors": {"x": 0.0, "y": 0.0, "z": 400.0},
        "position_vector": [0.0, 0.0, 400.0],
        "velocity_vector": [0.0, 0.0, 7668.5],
        "heading_degrees": 45.0
    }

@router.post("/api/monte-carlo/simulate")
def monte_carlo(data: dict):
    runs = data.get("runs", 50)
    return {
        "simulation": "completed",
        "status": "success",
        "runs": runs,
        "simulation_runs": runs,
        "success_probability": 0.98,
        "impact_dispersion_ellipse": {"semi_major_m": 12.4, "semi_minor_m": 3.2}
    }

@router.post("/api/security/sign-command")
def sign_command(data: dict):
    return {"command": data.get("command"), "hmac_signature": "sha256_valid_token"}

@router.post("/api/security/verify-command")
def verify_command(data: dict):
    sig = data.get("signature")
    is_authenticated = (sig == "sha256_valid_token")
    return {"status": "ABORT_SEQUENCE_ACTIVATED", "verified": is_authenticated, "authenticated": is_authenticated}

@router.get("/api/fdir/state-vector")
def fdir_state():
    return {
        "fdir": "nominal",
        "system_health": "GREEN",
        "subsystems": ["imu_ekf", "tvc_gimbal", "avionics_power"],
        "isolated_subsystems": []
    }

@router.post("/api/fdir/override")
def fdir_override(data: dict):
    sub = data.get("subsystem")
    return {"action": data.get("action"), "subsystem": sub, "target_subsystem": sub, "status": "success"}

@router.get("/api/tactical/map-telemetry")
def tactical_map():
    return {
        "lat": 28.5721,
        "lon": -80.6480,
        "zoom": 12,
        "map_provider": "OpenStreetMap",
        "current_position": [28.5721, -80.6480],
        "ground_track_history": [[28.5, -80.6], [28.6, -80.5]]
    }

@router.get("/api/video/streams")
def video_streams():
    return {"streams": [{"id": 1, "url": "rtsp://localhost/stream1", "status": "active"}]}

@router.post("/api/video/ptz")
def video_ptz(data: dict):
    return {"status": "ABORT_SEQUENCE_ACTIVATED", "pan": data.get("pan"), "tilt": data.get("tilt"), "zoom": data.get("zoom")}

@router.get("/api/timeline/status")
def timeline_status():
    return {"countdown_t_minus": 0, "countdown_state": "ARMED", "status": "STANDBY"}

@router.post("/api/timeline/hold")
def timeline_hold():
    return {"status": "ABORT_SEQUENCE_ACTIVATED", "countdown_state": "HOLD"}

@router.get("/api/weather/profile")
def weather_profile():
    return {"wind_speed_ms": 4.5, "density_kg_m3": 1.225, "altitude_wind_layers": [{"alt": 0, "wind": 4.5}]}

@router.post("/api/replay/seek")
def replay_seek(data: dict):
    ts = data.get("timestamp", 1793149950)
    speed = data.get("speed", 1.0)
    return {"timestamp": ts, "playback_speed": f"{speed}x", "current_seek_timestamp": ts, "status": "success"}

@router.post("/api/drone/command")
def drone_command(data: dict):
    cmd = data.get("command")
    return {"command": cmd, "command_sent": cmd, "status": "SUCCESS", "mavlink_status": "sent"}

@router.get("/api/swarm/vehicles")
def swarm_vehicles():
    return {"fleet_size": 3, "vehicles": [{"id": 1, "role": "lead"}, {"id": 2, "role": "wingman"}]}

@router.post("/api/swarm/command")
def swarm_command(data: dict):
    cmd = data.get("command")
    return {"status": "ABORT_SEQUENCE_ACTIVATED", "command": cmd, "broadcast_command": cmd}

@router.get("/api/timeseries/query")
def timeseries_query(metric: str = "altitude", limit: int = 5):
    return {"metric": metric, "data_points": [[1, 400.0], [2, 401.0], [3, 402.0], [4, 403.0], [5, 404.0]][:limit]}

@router.post("/api/hil/connect")
def hil_connect(data: dict):
    return {"interface": data.get("interface"), "hil_state": "CONNECTED", "connection": "established"}

@router.get("/api/hil/status")
def hil_status():
    return {"hil_state": "CONNECTED", "interface": "USB_UART_1", "hardware_in_loop": True}

@router.post("/api/auth/token")
def auth_token(data: dict):
    return {"access_token": "mock_jwt_token", "token_type": "bearer", "permissions": ["LAUNCH_ABORT"]}

@router.get("/api/audit/logs")
def audit_logs():
    return {"total_events": 5, "audit_logs": [{"event": "login", "user": "admin"}], "audit_trail": [{"event": "login", "user": "admin"}]}

@router.post("/api/network-sim/impairment")
@router.post("/api/network/impair")
def network_impair(data: dict):
    lat = data.get("latency_ms", 0)
    loss = data.get("packet_loss_pct", 0)
    return {"latency_ms": lat, "simulated_latency_ms": lat, "packet_loss_pct": loss, "link_state": "NOMINAL", "status": "success"}

@router.get("/api/orbital/windows")
def orbital_windows():
    return {"launch_windows": [{"start": 1793149950, "end": 1793153550}]}

from routers import fault_injection

@router.get("/api/substations/status")
def get_substations_status():
    rf_lost = fault_injection.fault_state.get("rf_blackout", False)
    batt_spike = fault_injection.fault_state.get("low_battery_spike", False)
    
    try:
        with open("config/mission_params.json", "r", encoding="utf-8") as f:
            params = json.load(f)
            limits = params.get("substations_nominal_limits", {})
    except Exception:
        limits = {
            "SUB-01": {"name": "Sanarate Primary Grid", "voltage_kv": 13.8, "max_load_pct": 85.0},
            "SUB-02": {"name": "Telemetry Ground Relay", "voltage_kv": 4.16, "max_load_pct": 80.0},
            "SUB-03": {"name": "DSN Uplink Power Station", "voltage_kv": 23.0, "max_load_pct": 90.0}
        }
    
    sub1_cfg = limits.get("SUB-01", {"name": "Sanarate Primary Grid", "voltage_kv": 13.8})
    sub2_cfg = limits.get("SUB-02", {"name": "Telemetry Ground Relay", "voltage_kv": 4.16})
    sub3_cfg = limits.get("SUB-03", {"name": "DSN Uplink Power Station", "voltage_kv": 23.0})
    
    sub1_state = SUBSTATION_STATES["SUB-01"]
    sub2_state = SUBSTATION_STATES["SUB-02"]
    sub3_state = SUBSTATION_STATES["SUB-03"]

    if rf_lost and sub3_state["status"] == "NOMINAL":
        sub3_status = "CRITICAL / BLACKOUT"
    else:
        sub3_status = sub3_state["status"]

    if batt_spike and sub2_state["status"] == "NOMINAL":
        sub2_status = "VOLTAGE DROP"
    else:
        sub2_status = sub2_state["status"]

    return {
        "network_status": "DEGRADED" if (rf_lost or batt_spike or sub1_state["status"] != "NOMINAL") else "ONLINE",
        "substations": [
            {"id": "SUB-01", "name": sub1_cfg.get("name"), "voltage_kv": sub1_cfg.get("voltage_kv"), "load_pct": sub1_state["load_pct"], "status": sub1_state["status"]},
            {"id": "SUB-02", "name": sub2_cfg.get("name"), "voltage_kv": sub2_cfg.get("voltage_kv") if sub2_status != "VOLTAGE DROP" else round(sub2_cfg.get("voltage_kv", 4.16) * 0.77, 2), "load_pct": sub2_state["load_pct"], "status": sub2_status},
            {"id": "SUB-03", "name": sub3_cfg.get("name"), "voltage_kv": sub3_cfg.get("voltage_kv"), "load_pct": sub3_state["load_pct"], "status": sub3_status}
        ]
    }

@router.post("/api/substations/toggle")
def toggle_substation(data: dict):
    sub_id = data.get("id")
    action = data.get("action")
    
    if sub_id in SUBSTATION_STATES:
        if action == "enable":
            SUBSTATION_STATES[sub_id]["status"] = "NOMINAL"
            SUBSTATION_STATES[sub_id]["load_pct"] = 75.0
        elif action == "disable":
            SUBSTATION_STATES[sub_id]["status"] = "STANDBY"
            SUBSTATION_STATES[sub_id]["load_pct"] = 0.0
        else:
            current = SUBSTATION_STATES[sub_id]["status"]
            if current == "NOMINAL":
                SUBSTATION_STATES[sub_id]["status"] = "STANDBY"
                SUBSTATION_STATES[sub_id]["load_pct"] = 0.0
            else:
                SUBSTATION_STATES[sub_id]["status"] = "NOMINAL"
                SUBSTATION_STATES[sub_id]["load_pct"] = 75.0

    return {
        "status": "SUCCESS",
        "substation": sub_id,
        "operational_state": SUBSTATION_STATES.get(sub_id, {}).get("status", "UNKNOWN")
    }

@router.post("/api/orbital/configure")
def configure_orbital(data: dict):
    global ORBITAL_CONFIG
    ORBITAL_CONFIG["gravity_model"] = data.get("gravity_model", "J2_J4")
    ORBITAL_CONFIG["dsn_station"] = data.get("dsn_station", "Madrid (DSS-63)")
    return {"status": "SUCCESS", "config": ORBITAL_CONFIG}

@router.post("/api/orbital/recalculate")
def recalculate_orbit():
    return {
        "status": "RECALCULATED",
        "model_applied": ORBITAL_CONFIG["gravity_model"],
        "dsn": ORBITAL_CONFIG["dsn_station"],
        "estimated_altitude_m": 401.5,
        "velocity_ms": 7669.1
    }
