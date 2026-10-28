(function() {
    // 1. Tarjeta de Propulsión Iónica de Efecto Hall (HET)
    const hetCard = document.createElement('div');
    hetCard.className = 'card';
    hetCard.style.border = '1px solid #06b6d4';
    hetCard.innerHTML = `
        <h3>🚀 Propulsión Iónica & Efecto Hall (HET Ion Thruster)</h3>
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; text-align: center; margin-top: 8px;">
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #22d3ee;">Flujo Xenón (Xe)</span><br><strong style="color: #34d399;">5.2 mg/s</strong>
            </div>
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #22d3ee;">Voltaje de Ánodo</span><br><strong style="color: #38bdf8;">300 V DC</strong>
            </div>
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #22d3ee;">Impulso Específico (Isp)</span><br><strong style="color: #facc15;">1850 s</strong>
            </div>
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #22d3ee;">Empuje Nominal</span><br><strong style="color: #34d399;">85.4 mN</strong>
            </div>
        </div>
    `;

    // 2. Tarjeta de Retardo de Luz (RTLT) y Desplazamiento Doppler
    const rtltCard = document.createElement('div');
    rtltCard.className = 'card';
    rtltCard.style.border = '1px solid #f59e0b';
    rtltCard.innerHTML = `
        <h3>📡 Espacio Profundo: RTLT (Round-Trip Light Time) & Doppler</h3>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; text-align: center; margin-top: 8px;">
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #fbbf24;">Retardo de Luz (RTLT)</span><br><strong style="color: #38bdf8;">1.34 segundos</strong>
            </div>
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #fbbf24;">Desplazamiento Doppler</span><br><strong style="color: #34d399;">+42.8 kHz</strong>
            </div>
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #fbbf24;">Relación Portadora/Ruido</span><br><strong style="color: #34d399;">54.2 dB-Hz</strong>
            </div>
        </div>
    `;

    const container = document.body.querySelector('.container');
    if (container) {
        container.appendChild(hetCard);
        container.appendChild(rtltCard);
    }
})();
