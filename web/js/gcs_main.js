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

    let currentLat = pkt.lat;
    let currentLon = pkt.lon;

    if (!currentLat || !currentLon) {
        const timeOffset = (pkt.time || 0) * 0.0008;
        currentLat = 14.7883 + Math.sin(timeOffset) * 0.0035;
        currentLon = -90.1988 + Math.cos(timeOffset) * 0.0035;
    }

    const pos = [currentLat, currentLon];
    droneMarker.setLatLng(pos);
    trajectoryPath.addLatLng(pos);

    if (pkt.alerts && pkt.alerts.length > 0) {
        pkt.alerts.forEach(alert => {
            logConsole(`[ALERTA FSW] ${alert}`);
        });
    }
};

async function startMission() {
    if (dynamicWaypoints.length === 0) {
        alert("Haz clic en el mapa para trazar al menos un waypoint antes de iniciar.");
        return;
    }

    await fetch('/api/mission/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ waypoints: dynamicWaypoints })
    });

    logConsole(`[COMANDO] Misión iniciada con ${dynamicWaypoints.length} waypoints de ruta.`);
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
        clearMissionPath();
        dynamicWaypoints = r.waypoints;
        
        dynamicWaypoints.forEach((wp, index) => {
            const marker = L.circleMarker([wp.lat, wp.lon], { radius: 6, color: '#38bdf8', fillColor: '#38bdf8', fillOpacity: 0.9 }).addTo(map)
             .bindPopup(`<b>${wp.name || 'WP Cargado'}</b><br>Lat: ${wp.lat.toFixed(4)}<br>Lon: ${wp.lon.toFixed(4)}`);
            waypointMarkers.push(marker);
        });

        renderWaypointsTable();
        alert(`Misión cargada (${dynamicWaypoints.length} waypoints).`);
    } else {
        alert("No hay misiones guardadas.");
    }
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
