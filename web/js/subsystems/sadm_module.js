(function() {
    const sadmCard = document.createElement('div');
    sadmCard.className = 'card';
    sadmCard.style.border = '1px solid #eab308';
    sadmCard.innerHTML = `
        <h3>☀️ SADM (Solar Array Drive Mechanism & Power Tracking)</h3>
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; text-align: center; margin-top: 8px;">
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #fde047;">Ángulo Solar Panel A</span><br><strong style="color: #38bdf8;">+45.2° (TRACKING)</strong>
            </div>
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #fde047;">Ángulo Solar Panel B</span><br><strong style="color: #38bdf8;">+45.1° (TRACKING)</strong>
            </div>
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #fde047;">Corriente de Salida</span><br><strong style="color: #34d399;">14.2 Amperios</strong>
            </div>
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #fde047;">Eficiencia Fotovoltaica</span><br><strong style="color: #34d399;">29.8% (GaInP/GaAs)</strong>
            </div>
        </div>
    `;
    const container = document.body.querySelector('.container');
    if (container) container.appendChild(sadmCard);
})();
