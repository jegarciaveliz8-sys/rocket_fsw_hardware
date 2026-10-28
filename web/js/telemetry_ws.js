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
            { label: 'Velocidad (km/h)', data: [], borderColor: '#38bdf8', fill: false }
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
        document.getElementById("ws-status").innerText = "CONNECTED (LIVE)";
        document.getElementById("ws-status").style.color = "#34d399";
        logEvent("Enlace CCSDS en vivo establecido con MCC.", "INFO");
    };

    ws.onmessage = function(event) {
        if (replayActive) return;
        const data = JSON.parse(event.data);
        selectedMissionForPDF = data.mission_id || 1;

        document.getElementById("metric-alt").innerText = (data.altitude || 0) + " km";
        document.getElementById("metric-vel").innerText = (data.velocity || 0) + " km/h";
        document.getElementById("metric-pc").innerText = (data.pressure || 15.4) + " MPa";
        document.getElementById("metric-dsn").innerText = data.dsn_station || "Cape Canaveral";
        document.getElementById("fsw-sequence").innerText = data.status || "STANDBY";
        document.getElementById("metric-temp").innerText = (38.4 + (data.time || 0) * 0.05).toFixed(1) + " °C";
        
        const blackoutEl = document.getElementById("metric-blackout");
        blackoutEl.innerText = data.blackout_status || "NOMINAL";
        blackoutEl.style.color = (data.blackout_status || "").includes("BLACKOUT") ? "#f87171" : "#34d399";

        let loxPct = Math.max(0, 100 - (data.time || 0) * 0.8).toFixed(1);
        let rp1Pct = Math.max(0, 100 - (data.time || 0) * 0.9).toFixed(1);
        document.getElementById("lox-val").innerText = loxPct + "%";
        document.getElementById("lox-fill").style.width = loxPct + "%";
        document.getElementById("rp1-val").innerText = rp1Pct + "%";
        document.getElementById("rp1-fill").style.width = rp1Pct + "%";

        document.getElementById("orbit-a").innerText = (data.orbit_a || 6371.0) + " km";
        document.getElementById("orbit-e").innerText = data.orbit_e || 0.0000;
        document.getElementById("orbit-i").innerText = (data.orbit_i || 28.5) + "°";

        document.getElementById("fdir-fault").innerText = data.injected_fault || "NONE";
        document.getElementById("fdir-action").innerText = data.fdir_action || "NOMINAL";
        document.getElementById("ccsds-hex").innerText = data.ccsds_frame || "081AC0000018...";

        updateRocketAttitude(data.pitch, data.yaw, data.roll);
        updateGPSPosition(data.lat, data.lon);

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
            document.getElementById("ws-status").innerText = "DISCONNECTED";
            document.getElementById("ws-status").style.color = "#f87171";
            setTimeout(connectWS, 3000);
        }
    };
}

function sendCommand(cmd) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ command: cmd }));
        logEvent(`Comando MCC enviado: ${cmd}`, "INFO");
    }
}

function triggerFTS() {
    let code = prompt("🚨 INGRESE CÓDIGO DE DOBLE LLAVE FTS PARA ABORTO DE EMERGENCIA (Ej: ODYSSEY-ABORT):");
    if (code === "ODYSSEY-ABORT") {
        sendCommand("ABORT");
        logEvent("¡SISTEMA FTS ACTIVADO! Destrucción de seguridad ejecutada.", "ERROR");
    } else {
        logEvent("Código FTS incorrecto. Aborto cancelado.", "WARN");
    }
}

async function loadMissionList() {
    try {
        const res = await fetch("/api/missions");
        const data = await res.json();
        const select = document.getElementById("mission-select");
        select.innerHTML = "";
        if (data.missions && data.missions.length > 0) {
            data.missions.forEach(id => {
                const opt = document.createElement("option");
                opt.value = id;
                opt.innerText = `Misión Histórica #${id}`;
                select.appendChild(opt);
            });
            selectedMissionForPDF = select.value || data.missions[data.missions.length - 1];
        } else {
            select.innerHTML = `<option value="">No hay misiones grabadas</option>`;
        }
    } catch (e) {
        console.error("Error cargando misiones:", e);
    }
}

function downloadPDF() {
    const missionId = document.getElementById("mission-select").value || selectedMissionForPDF || 1;
    window.location.href = `/export/pdf/${missionId}`;
}

connectWS();
loadMissionList();
