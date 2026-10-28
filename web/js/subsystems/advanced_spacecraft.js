(function() {
    // 1. Crear tarjeta de Constelación ISL (Enlaces Láser Inter-Satelitales)
    const islCard = document.createElement('div');
    islCard.className = 'card';
    islCard.style.border = '1px solid #06b6d4';
    islCard.innerHTML = `
        <h3>🛰️ Enlace Óptico Láser Inter-Satelital (ISL Mesh Network)</h3>
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; text-align: center; margin-top: 8px;">
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #94a3b8;">Nodo Primario</span><br><strong style="color: #06b6d4;">SAT-ALPHA (01)</strong>
            </div>
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #94a3b8;">Nodo Enjambre (Cross-Link)</span><br><strong style="color: #38bdf8;">SAT-BETA (02) - LOCK</strong>
            </div>
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #94a3b8;">Banda Láser ISL</span><br><strong style="color: #34d399;">1550 nm / 10 Gbps</strong>
            </div>
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #94a3b8;">Latencia Inter-Nodo</span><br><strong style="color: #facc15;">1.42 ms</strong>
            </div>
        </div>
    `;

    // 2. Crear tarjeta de Inferencia de Ingesta ML & Ventanas de Transferencia Orbital
    const mlCard = document.createElement('div');
    mlCard.className = 'card';
    mlCard.style.border = '1px solid #ec4899';
    mlCard.innerHTML = `
        <h3>🧠 Motor ML Predictivo de Anomalías & Planificador $\\Delta v$ Lambert</h3>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; text-align: center; margin-top: 8px;">
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #ec4899;">Índice de Salud Preventiva</span><br><strong style="color: #34d399;">99.98% (NOMINAL)</strong>
            </div>
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #ec4899;">Próxima Ventana $\\Delta v$</span><br><strong style="color: #38bdf8;">T+00:42:15 (Hohmann)</strong>
            </div>
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #ec4899;">Margen Térmico Carenado</span><br><strong style="color: #34d399;">+142.8 °C (SEGURO)</strong>
            </div>
        </div>
    `;

    // Insertar las tarjetas en la retícula
    const container = document.body.querySelector('.container');
    if (container) {
        container.insertBefore(islCard, container.children[4]);
        container.insertBefore(mlCard, container.children[5]);
    }
})();
