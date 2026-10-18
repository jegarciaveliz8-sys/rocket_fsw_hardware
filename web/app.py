import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI(title="Rocket Ground Station Web")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Estación Terrena - Rocket FSW</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: Arial, sans-serif; background: #0d1117; color: #c9d1d9; text-align: center; margin: 0; padding: 20px; }
        .card { background: #161b22; border: 1px solid #30363d; border-radius: 8px; display: inline-block; margin: 10px; padding: 20px; width: 200px; }
        .value { font-size: 24px; font-weight: bold; color: #58a6ff; }
        .chart-container { width: 80%; max-width: 800px; margin: 20px auto; background: #161b22; padding: 20px; border-radius: 8px; border: 1px solid #30363d; }
    </style>
</head>
<body>
    <h1>ESTACIÓN TERRENA WEB - GNC & FSW</h1>
    <div>
        <div class="card"><div>Estado FSM</div><div id="fsm-state" class="value">PAD_IDLE</div></div>
        <div class="card"><div>Altitud</div><div id="alt" class="value">0.0 m</div></div>
        <div class="card"><div>Velocidad</div><div id="vel" class="value">0.0 m/s</div></div>
        <div class="card"><div>Aceleración</div><div id="accel" class="value">0.0 G</div></div>
    </div>
    
    <div class="chart-container">
        <canvas id="telemetryChart"></canvas>
    </div>

    <script>
        const ctx = document.getElementById('telemetryChart').getContext('2d');
        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Altitud (m)',
                    data: [],
                    borderColor: '#58a6ff',
                    tension: 0.1
                }]
            },
            options: { responsive: true }
        });

        const ws = new WebSocket("ws://localhost:8000/ws");
        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            document.getElementById('fsm-state').innerText = data.state;
            document.getElementById('alt').innerText = data.altitude.toFixed(1) + " m";
            document.getElementById('vel').innerText = data.velocity.toFixed(1) + " m/s";
            document.getElementById('accel').innerText = data.acceleration.toFixed(1) + " G";

            if (chart.data.labels.length > 20) {
                chart.data.labels.shift();
                chart.data.datasets[0].data.shift();
            }
            chart.data.labels.push(data.time);
            chart.data.datasets[0].data.push(data.altitude);
            chart.update();
        };
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def get_index():
    return HTML_TEMPLATE

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    t = 0
    try:
        while True:
            t += 1
            # Simulación de datos de vuelo dinámicos
            alt = max(0.0, 180.0 * (1 - ((t - 6)**2 / 36.0))) if t <= 12 else 0.0
            vel = 65.0 - (t * 6.0)
            accel = 5.8 if t == 1 else 0.1
            state = "BOOST" if t < 3 else ("COASTING" if t < 6 else ("APOGEE" if t < 8 else "DESCENT"))
            
            payload = {
                "time": t,
                "state": state,
                "altitude": alt,
                "velocity": vel,
                "acceleration": accel
            }
            await websocket.send_text(json.dumps(payload))
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        print("Cliente desconectado de la Estación Terrena Web.")
