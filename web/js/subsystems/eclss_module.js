(function() {
    const eclssCard = document.createElement('div');
    eclssCard.className = 'card';
    eclssCard.style.border = '1px solid #14b8a6';
    eclssCard.innerHTML = `
        <h3>👨‍🚀 ECLSS (Environmental Control & Life Support System)</h3>
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; text-align: center; margin-top: 8px;">
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #2dd4bf;">Presión de Cabina</span><br><strong style="color: #34d399;">101.3 kPa (1 atm)</strong>
            </div>
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #2dd4bf;">Nivel CO2 (Scrubber)</span><br><strong style="color: #38bdf8;">0.25% (NOMINAL)</strong>
            </div>
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #2dd4bf;">Humedad Relativa</span><br><strong style="color: #34d399;">48.2%</strong>
            </div>
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #2dd4bf;">Temp. Interna Módulo</span><br><strong style="color: #facc15;">21.4 °C</strong>
            </div>
        </div>
    `;
    const container = document.body.querySelector('.container');
    if (container) container.appendChild(eclssCard);
})();
