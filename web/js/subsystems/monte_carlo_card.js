(function() {
    const container = document.createElement('div');
    container.className = 'card';
    container.style.border = '1px solid #a855f7';
    container.innerHTML = `
        <h3>🎲 Matriz Monte Carlo & Dispersión (N=1000)</h3>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; text-align: center; margin-top: 8px;">
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #a855f7;">Dispersión Δv</span><br><strong style="color: #38bdf8;">± 1.24 m/s</strong>
            </div>
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #a855f7;">Éxito LEO</span><br><strong style="color: #34d399;">99.84%</strong>
            </div>
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #a855f7;">Deriva Órbita</span><br><strong style="color: #facc15;">0.04 km/orb</strong>
            </div>
        </div>
    `;
    document.body.querySelector('.container').appendChild(container);
})();
