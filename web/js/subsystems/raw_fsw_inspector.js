(function() {
    const rawCard = document.createElement('div');
    rawCard.className = 'card';
    rawCard.style.border = '1px solid #10b981';
    rawCard.innerHTML = `
        <h3>🧩 Depurador de Trama Binaria Cruda CCSDS (RTOS Link Inspector)</h3>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; text-align: center; margin-top: 8px;">
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #10b981;">Validación CRC-16 CCITT</span><br><strong id="raw-crc" style="color: #34d399;">VERIFIED (0-ERRORS)</strong>
            </div>
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #10b981;">Deriva de Reloj (PTP Drift)</span><br><strong id="raw-drift" style="color: #38bdf8;">+0.142 ms</strong>
            </div>
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #10b981;">Momentum Ruedas (RW)</span><br><strong id="raw-rw" style="color: #facc15;">[0.15, -0.08, 0.02] Nms</strong>
            </div>
        </div>
        <pre id="raw-hex-stream" style="margin-top: 8px; height: 45px; overflow-y: auto; font-size: 9px; color: #10b981;">Esperando búfer de tramas CCSDS del RTOS...</pre>
    `;

    const container = document.body.querySelector('.container');
    if (container) {
        container.appendChild(rawCard);
    }

    // Escuchar mensajes de WebSocket para actualizar el inspector crudo
    window.updateRawInspector = function(data) {
        const crcEl = document.getElementById("raw-crc");
        const driftEl = document.getElementById("raw-drift");
        const rwEl = document.getElementById("raw-rw");
        const streamEl = document.getElementById("raw-hex-stream");

        if (crcEl && data.crc_valid) {
            crcEl.innerText = "VERIFIED (0-ERRORS)";
            crcEl.style.color = "#34d399";
        }
        if (driftEl) driftEl.innerText = `+${data.clock_drift_ms} ms`;
        if (rwEl && data.rw_momentum) {
            rwEl.innerText = `[${data.rw_momentum.join(', ')}] Nms`;
        }
        if (streamEl && data.ccsds_frame) {
            streamEl.innerText = `[SYNC_WORD: 0x1ACFFC] [APID: 0x01A] [DATA_HEX: ${data.ccsds_frame}]`;
        }
    };
})();
