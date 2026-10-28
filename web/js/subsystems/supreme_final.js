(function() {
    // 1. Tarjeta de Seguridad FTS de Doble Llave y HMAC Authority
    const ftsCard = document.createElement('div');
    ftsCard.className = 'card';
    ftsCard.style.border = '1px solid #ef4444';
    ftsCard.innerHTML = `
        <h3>🔐 FTS Safety Authority & Control de Seguridad Range Safety</h3>
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; text-align: center; margin-top: 8px;">
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #94a3b8;">Estado Llave A (RSO-1)</span><br><strong style="color: #34d399;">ARMED / VALIDATED</strong>
            </div>
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #94a3b8;">Estado Llave B (RSO-2)</span><br><strong style="color: #34d399;">ARMED / VALIDATED</strong>
            </div>
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #94a3b8;">HMAC Signature</span><br><strong style="color: #38bdf8;">0x8F9A...C412</strong>
            </div>
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #94a3b8;">FTS Command Lock</span><br><strong style="color: #f87171;">READY (DESTRUCT OPTION)</strong>
            </div>
        </div>
    `;

    // 2. Tarjeta Quaternions & Ablación de Escudo Térmico TPS
    const tpsCard = document.createElement('div');
    tpsCard.className = 'card';
    tpsCard.style.border = '1px solid #f97316';
    tpsCard.innerHTML = `
        <h3>🔥 Actitud Quaternion ($q_0..q_3$) & Escudo Térmico TPS</h3>
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; text-align: center; margin-top: 8px;">
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #f97316;">Quaternions IMU</span><br><strong style="color: #38bdf8;">[0.707, 0.0, 0.707, 0.0]</strong>
            </div>
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #f97316;">Ablación TPS</span><br><strong style="color: #34d399;">0.12 mm/s (Márgenes Nominales)</strong>
            </div>
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #f97316;">Flujo Térmico Reingreso</span><br><strong style="color: #facc15;">1.2 MW/m²</strong>
            </div>
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #f97316;">Densidad de Plasma</span><br><strong style="color: #34d399;">Nivel 2 (Banda X Carga)</strong>
            </div>
        </div>
    `;

    const container = document.body.querySelector('.container');
    if (container) {
        container.appendChild(ftsCard);
        container.appendChild(tpsCard);
    }
})();
