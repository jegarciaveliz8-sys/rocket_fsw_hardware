(function() {
    const card = document.createElement('div');
    card.className = 'card';
    card.style.border = '1px solid #ec4899';
    card.innerHTML = `
        <h3>🧠 Modelo LSTM Predictivo de Fallas (Deep Learning Anomaly Forecast)</h3>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; text-align: center; margin-top: 8px;">
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #f472b6;">Riesgo Térmico Batería</span><br><strong style="color: #34d399;">0.01% (Bajo)</strong>
            </div>
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #f472b6;">Ventana de Alerta Previa</span><br><strong style="color: #38bdf8;">+45 minutos sin fallas</strong>
            </div>
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #f472b6;">Inferencia LSTM Tensor</span><br><strong style="color: #34d399;">OPTIMAL (Loss: 0.002)</strong>
            </div>
        </div>
    `;
    const container = document.body.querySelector('.container');
    if (container) container.appendChild(card);
})();
