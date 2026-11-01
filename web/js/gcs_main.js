// --- LÓGICA PRINCIPAL GCS ODYSSEY-1 ---
let dynamicWaypoints = [];

document.addEventListener("DOMContentLoaded", () => {
    initWebSocket();
});

function initWebSocket() {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
    const ws = new WebSocket(wsProtocol + window.location.host + '/ws/telemetry');

    ws.onmessage = function(event) {
        const pkt = JSON.parse(event.data);
        
        document.getElementById("val-alt").innerText = pkt.altitude + " m";
        document.getElementById("val-vel").innerText = pkt.velocity + " m/s";
        document.getElementById("val-pc").innerText = pkt.chamber_pressure + " MPa";
        document.getElementById("val-bat").innerText = pkt.battery_pct + " %";
        document.getElementById("lbl-status").innerText = pkt.status;
        document.getElementById("lbl-met").innerText = `MET: T+${String(Math.floor(pkt.time/60)).padStart(2,'0')}:${String(pkt.time%60).padStart(2,'0')}`;
        
        document.getElementById("val-pitch").innerText = (pkt.pitch || 0) + "°";
        document.getElementById("val-roll").innerText = (pkt.roll || 0) + "°";
        document.getElementById("val-yaw").innerText = (pkt.yaw || 0) + "°";
        document.getElementById("val-ccsds").innerText = pkt.ccsds_frame;

        if (window.updateDronePosition && pkt.lat && pkt.lon) {
            window.updateDronePosition(pkt.lat, pkt.lon);
        }

        if (pkt.alerts && pkt.alerts.length > 0) {
            pkt.alerts.forEach(alert => {
                logConsole(`[ALERTA FSW] ${alert}`);
            });
        }
    };
}

async function startMission() {
    await fetch('/api/mission/start', { method: 'POST' });
    logConsole("[COMANDO] Misión autónoma iniciada en Sanarate.");
}

async function abortMission() {
    await fetch('/api/mission/abort', { method: 'POST' });
    logConsole("[COMANDO] Misión abortada / RTL forzado.");
}

async function toggleFault(faultName, checkbox) {
    await fetch('/api/fault/inject', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fault: faultName, active: checkbox.checked })
    });
    logConsole(`[INYECCIÓN] ${faultName} -> ${checkbox.checked ? 'ACTIVADO' : 'DESACTIVADO'}`);
}

async function saveCurrentMission() {
    if (dynamicWaypoints.length === 0) { alert("No hay waypoints."); return; }
    const res = await fetch('/api/mission-planner/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ waypoints: dynamicWaypoints })
    });
    const r = await res.json();
    alert(r.message);
}

async function loadSavedMission() {
    const res = await fetch('/api/mission-planner/load');
    const r = await res.json();
    if (r.status === "SUCCESS") {
        dynamicWaypoints = r.waypoints;
        renderWaypointsList();
        alert(`Misión cargada (${dynamicWaypoints.length} waypoints).`);
    } else {
        alert("No hay misiones guardadas.");
    }
}

function clearMissionPath() {
    dynamicWaypoints = [];
    renderWaypointsList();
    logConsole("[MAPA] Waypoints limpiados.");
}

function renderWaypointsList() {
    const container = document.getElementById("waypoints-list-container");
    if (!container) return;
    if (dynamicWaypoints.length === 0) { container.innerHTML = "No hay waypoints."; return; }
    let html = "";
    dynamicWaypoints.forEach((wp, i) => {
        html += `<div><b>WP${i}:</b> ${wp.lat.toFixed(4)}, ${wp.lon.toFixed(4)}</div>`;
    });
    container.innerHTML = html;
}

async function queryAICopilot() {
    const promptInput = document.getElementById("ai-prompt-input");
    const chatBox = document.getElementById("ai-chat-response");
    const text = promptInput.value;
    if(!text) return;

    chatBox.innerHTML += `<br><b>Tú:</b> ${text}`;
    promptInput.value = "";

    try {
        const res = await fetch('/api/ai/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt: text })
        });
        const data = await res.json();
        chatBox.innerHTML += `<br><b>AI:</b> ${data.response}`;
        chatBox.scrollTop = chatBox.scrollHeight;
    } catch (err) {
        chatBox.innerHTML += `<br><b>AI:</b> Error de conexión con el copiloto.`;
    }
}

function logConsole(text) {
    const consoleBox = document.getElementById('mcc-console');
    if (consoleBox) {
        const timeStr = new Date().toLocaleTimeString();
        consoleBox.innerHTML += `<br>[${timeStr}] ${text}`;
        consoleBox.scrollTop = consoleBox.scrollHeight;
    }
}
