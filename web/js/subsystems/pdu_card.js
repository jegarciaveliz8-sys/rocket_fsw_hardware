(function() {
    const container = document.createElement('div');
    container.className = 'card';
    container.style.border = '1px solid #3b82f6';
    container.innerHTML = `
        <h3>⚡ PDU & Aislamiento de Buses de Aviónica</h3>
        <div style="display: flex; gap: 8px; justify-content: center; margin-top: 8px;">
            <button onclick="toggleBus('AVIONICS')" style="background: #16a34a;" id="btn-bus-av">Bus Aviónica: ON</button>
            <button onclick="toggleBus('PAYLOAD')" style="background: #16a34a;" id="btn-bus-pl">Bus Carga Útil: ON</button>
            <button onclick="toggleBus('RADIO')" style="background: #16a34a;" id="btn-bus-rd">Bus Transmisor S/X: ON</button>
            <button onclick="toggleBus('THERMAL')" style="background: #16a34a;" id="btn-bus-th">Bus Calefactores: ON</button>
        </div>
    `;
    document.body.querySelector('.container').appendChild(container);

    window.toggleBus = function(busName) {
        const btnMap = { 'AVIONICS': 'btn-bus-av', 'PAYLOAD': 'btn-bus-pl', 'RADIO': 'btn-bus-rd', 'THERMAL': 'btn-bus-th' };
        const btn = document.getElementById(btnMap[busName]);
        if (!btn) return;
        if (btn.innerText.includes("ON")) {
            btn.innerText = `Bus ${busName}: OFF`;
            btn.style.background = "#dc2626";
        } else {
            btn.innerText = `Bus ${busName}: ON`;
            btn.style.background = "#16a34a";
        }
    };
})();
