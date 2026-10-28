(function() {
    const card = document.createElement('div');
    card.className = 'card';
    card.style.border = '1px solid #a855f7';
    card.innerHTML = `
        <h3>🛰️ Constelación Multi-Satelital (Walker Delta 24/3/1)</h3>
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; text-align: center; margin-top: 8px;">
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #d8b4fe;">Satélites Activos</span><br><strong style="color: #38bdf8;">24 / 24 LEO</strong>
            </div>
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #d8b4fe;">Red Mesh ISL</span><br><strong style="color: #34d399;">OPTIMAL (99.9%)</strong>
            </div>
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #d8b4fe;">Plano Orbital</span><br><strong style="color: #facc15;">Plane #02 / Phase A</strong>
            </div>
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #d8b4fe;">Handover Global</span><br><strong style="color: #34d399;">0 ms Drop</strong>
            </div>
        </div>
    `;
    const container = document.body.querySelector('.container');
    if (container) container.appendChild(card);
})();
