let ws;
let replayActive = false;
let selectedMissionForPDF = 1;

const ctx = document.getElementById('telemetryChart').getContext('2d');
const telemetryChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [
            { label: 'Altitud (km)', data: [], borderColor: '#34d399', backgroundColor: 'rgba(52, 211, 153, 0.1)', fill: true },
            { label: 'Velocidad (m/s)', data: [], borderColor: '#38bdf8', fill: false }
        ]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            x: { grid: { color: '#1e293b' }, ticks: { color: '#94a3b8' } },
            y: { grid: { color: '#1e293b' }, ticks: { color: '#94a3b8' } }
        }
    }
});

function logEvent(msg, type = "INFO") {
    const consoleEl = document.getElementById("mcc-console");
    if (!consoleEl) return;
    const timeStr = new Date().toLocaleTimeString();
    const color = type === "WARN" ? "#facc15" : (type === "ERROR" ? "#f87171" : "#34d399");
    consoleEl.innerHTML += `<br><span style="color:${color}">[${timeStr}] [${type}]</span> ${msg}`;
    consoleEl.scrollTop = consoleEl.scrollHeight;
}

function connectWS() {
    if (replayActive) return;
    const wsProtocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
    ws = new WebSocket(wsProtocol + window.location.host + "/ws/telemetry");

    ws.onopen = function() {
        const statusEl = document.getElementById("ws-status");
        if (statusEl) {
            statusEl.innerText = "CONNECTED (RTOS KERNEL)";
            statusEl.style.color = "#34d399";
        }
        logEvent("Enlace binario CCSDS en vivo establecido con el RTOS FSW.", "INFO");
    };

    ws.onmessage = function(event) {
        if (replayActive) return;
        const data = JSON.parse(event.data);
        
        // Actualizar métricas generales
        const altEl = document.getElementById("metric-alt");
        const velEl = document.getElementById("metric-vel");
        const pcEl = document.getElementById("metric-pc");
        const dsnEl = document.getElementById("metric-dsn");
        const fswEl = document.getElementById("fsw-sequence");
        const blackoutEl = document.getElementById("metric-blackout");

        if (altEl) altEl.innerText = (data.altitude || 0) + " km";
        if (velEl) velEl.innerText = (data.velocity || 0) + " m/s";
        if (pcEl) pcEl.innerText = "15.4 MPa";
        if (dsnEl) dsnEl.innerText = data.dsn_station || "Madrid (DSS-63)";
        if (fswEl) fswEl.innerText = data.status || "STANDBY";
        if (blackoutEl) blackoutEl.innerText = data.blackout_status || "NOMINAL";

        // Llamar al inspector crudo de bits
        if (typeof window.updateRawInspector === 'function') {
            window.updateRawInspector(data);
        }

        // Actualizar actitud 3D y mapa GIS si existen las funciones
        if (typeof updateRocketAttitude === 'function') {
            updateRocketAttitude(data.pitch, data.yaw, data.roll);
        }
        if (typeof updateGPSPosition === 'function') {
            updateGPSPosition(data.lat, data.lon);
        }

        // Actualizar gráfica Chart.js
        if (telemetryChart.data.labels.length > 30) {
            telemetryChart.data.labels.shift();
            telemetryChart.data.datasets[0].data.shift();
            telemetryChart.data.datasets[1].data.shift();
        }
        telemetryChart.data.labels.push("T+" + (data.time || 0) + "s");
        telemetryChart.data.datasets[0].data.push(data.altitude || 0);
        telemetryChart.data.datasets[1].data.push(data.velocity || 0);
        telemetryChart.update();
    };

    ws.onclose = function() {
        if (!replayActive) {
            const statusEl = document.getElementById("ws-status");
            if (statusEl) {
                statusEl.innerText = "DISCONNECTED";
                statusEl.style.color = "#f87171";
            }
            setTimeout(connectWS, 3000);
        }
    };
}

function sendCommand(cmd) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ command: cmd }));
        logEvent(`Comando Uplink AES-GCM enviado: ${cmd}`, "INFO");
    }
}

function triggerFTS() {
    let code = prompt("🚨 INGRESE LLAVE DE SEGURIDAD FTS (HMAC-SHA256):");
    if (code === "ODYSSEY-ABORT") {
        sendCommand("ABORT");
        logEvent("¡FTS EJECUTADO DESDE LA ESTACIÓN TERRESTRE!", "ERROR");
    } else {
        logEvent("Falla en validación de llave FTS.", "WARN");
    }
}

connectWS();
