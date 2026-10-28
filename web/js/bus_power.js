// --- Subsistema de Control y Aislamiento de Buses de Potencia (Power Distribution Unit - PDU) ---
const pduContainer = document.createElement('div');
pduContainer.className = 'card';
pduContainer.style.border = '1px solid #3b82f6';
pduContainer.innerHTML = `
    <h3>⚡ PDU & Aislamiento de Buses de Aviónica (Telemetry / Payload)</h3>
    <div style="display: flex; gap: 8px; justify-content: center; margin-top: 8px;">
        <button onclick="toggleBus('AVIONICS')" style="background: #16a34a;" id="btn-bus-av">Bus Aviónica: ON</button>
        <button onclick="toggleBus('PAYLOAD')" style="background: #16a34a;" id="btn-bus-pl">Bus Carga Útil: ON</button>
        <button onclick="toggleBus('RADIO')" style="background: #16a34a;" id="btn-bus-rd">Bus Transmisor S/X: ON</button>
        <button onclick="toggleBus('THERMAL')" style="background: #16a34a;" id="btn-bus-th">Bus Calefactores: ON</button>
    </div>
`;

document.addEventListener("DOMContentLoaded", () => {
    const mccLogCard = document.querySelector('.console-log').closest('.card');
    mccLogCard.parentNode.insertBefore(pduContainer, mccLogCard);
});

function toggleBus(busName) {
    const btnMap = {
        'AVIONICS': 'btn-bus-av',
        'PAYLOAD': 'btn-bus-pl',
        'RADIO': 'btn-bus-rd',
        'THERMAL': 'btn-bus-th'
    };
    const btnId = btnMap[busName];
    const btn = document.getElementById(btnId);
    if (btn.innerText.includes("ON")) {
        btn.innerText = `Bus ${busName}: OFF`;
        btn.style.background = "#dc2626";
        if (typeof logEvent === 'function') logEvent(`⚠️ ALERTA PDU: Bus ${busName} desconectado manualmente por operador.`, "WARN");
    } else {
        btn.innerText = `Bus ${busName}: ON`;
        btn.style.background = "#16a34a";
        if (typeof logEvent === 'function') logEvent(`INFO PDU: Bus ${busName} reenganchado y nominal.`, "INFO");
    }
}
