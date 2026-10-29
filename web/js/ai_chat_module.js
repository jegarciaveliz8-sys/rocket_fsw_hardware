// --- SUBSYSTEM: GEMINI AI COPILOT & TELEMETRY UI BINDINGS ---
let latestTelemetryData = { altitude: 398.24, velocity: 7667.53, pc: 15.4 };

async function askAI() {
    const input = document.getElementById("ai-input");
    const msgs = document.getElementById("ai-messages");
    const queryText = input.value.trim();
    if (!queryText) return;

    const userMsg = document.createElement("div");
    userMsg.innerHTML = `<span style="color: #58a6ff; font-weight: bold;">[Tú]:</span> ${queryText}`;
    msgs.appendChild(userMsg);
    input.value = "";
    msgs.scrollTop = msgs.scrollHeight;

    const loadingMsg = document.createElement("div");
    loadingMsg.innerHTML = `<span style="color: #facc15; font-weight: bold;">[AI]:</span> Analizando telemetría con Gemini...`;
    msgs.appendChild(loadingMsg);
    msgs.scrollTop = msgs.scrollHeight;

    try {
        const res = await fetch('/api/ai/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: queryText, telemetry_context: latestTelemetryData })
        });
        const data = await res.json();
        loadingMsg.innerHTML = `<span style="color: #34d399; font-weight: bold;">[Gemini AI]:</span> ${data.response}`;
    } catch (err) {
        loadingMsg.innerHTML = `<span style="color: #f87171; font-weight: bold;">[Error AI]:</span> No se pudo conectar con el backend de Gemini.`;
    }
    msgs.scrollTop = msgs.scrollHeight;
}

function handleAIPress(e) {
    if (e.key === 'Enter') askAI();
}
