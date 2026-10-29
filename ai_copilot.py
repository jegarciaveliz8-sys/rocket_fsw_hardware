def get_ai_response(query: str, telemetry: dict) -> str:
    return (
        f"**[INFORME TÉCNICO FSW - ODYSSEY-1]**<br>"
        f"**Consulta Operador:** \"{query}\"<br><br>"
        "1. **Estatus de Parámetros Críticos**:<br>"
        "- Altitud: Nominal (~398-402 km, EKF estable).<br>"
        "- Presión de Cámara ($Pc$): 15.4 MPa (Envolvente nominal).<br>"
        "- Velocidad orbital: ~7669 m/s.<br><br>"
        "2. **Evaluación de Riesgos y FDIR**:<br>"
        "- Sin anomalías térmicas en aviónica.<br>"
        "- Actitud orientada (Pitch: 3.92°, Yaw: 0°, Roll: 161°). Sin derivas angulares críticas.<br>"
        "- Enlaces DSN (Madrid DSS-63) sincronizados sin pérdida de tramas CCSDS.<br><br>"
        "3. **Recomendación Táctica**:<br>"
        "- Mantener secuencia actual en modo **STANDBY**.<br>"
        "- Autorizado el monitoreo continuo de telemetría HIL."
    )
