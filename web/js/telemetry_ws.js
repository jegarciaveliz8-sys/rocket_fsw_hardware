const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const wsUrl = `${wsProtocol}//${window.location.host}/ws/telemetry`;

let socket = null;
let missionStartTime = null;

function connectTelemetry() {
    socket = new WebSocket(wsUrl);

    socket.onopen = function() {
        const statusEl = document.getElementById('ws-status');
        if(statusEl) {
            statusEl.innerText = "CONNECTED (RTOS KERNEL)";
            statusEl.style.color = "#34d399";
        }
    };

    socket.onmessage = function(event) {
        const data = JSON.parse(event.data);

        document.getElementById('metric-alt').innerText = `${data.altitude} m`;
        document.getElementById('metric-vel').innerText = `${data.speed} m/s`;
        document.getElementById('metric-dsn').innerText = data.dsn_station;
        document.getElementById('fsw-sequence').innerText = data.status;

        // Actualizar Batería y Barra de Progreso
        const batVal = data.battery_pct !== undefined ? data.battery_pct : 100.0;
        document.getElementById('metric-battery').innerText = `${batVal}%`;
        const batteryFill = document.getElementById('battery-fill');
        if (batteryFill) {
            batteryFill.style.width = `${batVal}%`;
            batteryFill.style.backgroundColor = batVal < 30 ? '#f87171' : (batVal < 60 ? '#facc15' : '#34d399');
        }

        // Cronómetro MET (Mission Elapsed Time)
        if (data.status.includes("NAVIGATING") || data.status.includes("MISSION")) {
            if (!missionStartTime) missionStartTime = Date.now() - (data.time * 1000);
            const elapsedSec = Math.floor((Date.now() - missionStartTime) / 1000);
            const mins = String(Math.floor(elapsedSec / 60)).padStart(2, '0');
            const secs = String(elapsedSec % 60).padStart(2, '0');
            document.getElementById('met-timer').innerText = `T+${mins}:${secs}`;
        }

        document.getElementById('val-pitch').innerText = `${data.pitch}°`;
        document.getElementById('val-yaw').innerText = `${data.yaw}°`;
        document.getElementById('val-roll').innerText = `${data.roll}°`;

        // Actualizar Horizonte Artificial PFD
        if (typeof drawAttitudeIndicator === 'function') {
            drawAttitudeIndicator(data.pitch, data.roll, data.yaw);
        }

        document.getElementById('raw-ccsds').innerHTML = `FRAME: ${data.ccsds_frame}<br>CRC: VALID | Drifts: ${data.clock_drift_ms}ms`;

        // Actualizar posición en Mapa GIS
        if (typeof updateGPSPosition === 'function') {
            updateGPSPosition(data.lat, data.lon);
        }

        // Actualizar gráfica Chart.js
        if (typeof updateChartData === 'function') {
            updateChartData(data.time, data.altitude, data.speed);
        }

        if (data.alerts && data.alerts.length > 0) {
            const consoleBox = document.getElementById('mcc-console');
            if (consoleBox) {
                data.alerts.forEach(alert => {
                    const timeStr = new Date().toLocaleTimeString();
                    const alertClass = alert.level === 'CRITICAL' ? 'alert-critical' : 'alert-warning';
                    const logEntry = document.createElement('div');
                    logEntry.className = alertClass;
                    logEntry.innerHTML = `[${timeStr}] [ALERTA FSW - ${alert.level}] ${alert.message}`;
                    consoleBox.appendChild(logEntry);
                    consoleBox.scrollTop = consoleBox.scrollHeight;
                });
            }
        }
    };

    socket.onclose = function() {
        const statusEl = document.getElementById('ws-status');
        if(statusEl) {
            statusEl.innerText = "DISCONNECTED (RECONNECTING...)";
            statusEl.style.color = "#f87171";
        }
        setTimeout(connectTelemetry, 3000);
    };
}

async function sendCommand(cmd) {
    const consoleBox = document.getElementById('mcc-console');
    try {
        const response = await fetch('/api/commands/send', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command: cmd })
        });
        const result = await response.json();
        
        if(consoleBox) {
            const timeStr = new Date().toLocaleTimeString();
            consoleBox.innerHTML += `<br><span style="color: #38bdf8;">[${timeStr}] [COMANDO FSW] ${result.message}</span>`;
            consoleBox.scrollTop = consoleBox.scrollHeight;
        }
    } catch (error) {
        if(consoleBox) {
            consoleBox.innerHTML += `<br><span style="color: #f87171;">[ERROR] No se pudo enviar el comando ${cmd}.</span>`;
            consoleBox.scrollTop = consoleBox.scrollHeight;
        }
    }
}

function triggerFTS() {
    if(confirm("⚠️ ¿ESTÁS SEGURO DE ACTIVAR EL SISTEMA DE ABORTO (FTS)?")) {
        sendCommand('FTS_ABORT');
    }
}

window.addEventListener('DOMContentLoaded', () => {
    connectTelemetry();
});
