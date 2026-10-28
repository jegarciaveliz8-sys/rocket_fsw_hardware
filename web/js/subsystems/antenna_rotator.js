(function() {
    const card = document.createElement('div');
    card.className = 'card';
    card.style.border = '1px solid #14b8a6';
    card.innerHTML = `
        <h3>📡 Control de Antenas Ground Station (Rotator Az/El & Hamlib)</h3>
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; text-align: center; margin-top: 8px;">
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #2dd4bf;">Acimut (Az)</span><br><strong style="color: #38bdf8;">142.5°</strong>
            </div>
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #2dd4bf;">Elevación (El)</span><br><strong style="color: #34d399;">48.2°</strong>
            </div>
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #2dd4bf;">Modo Rotator</span><br><strong style="color: #facc15;">AUTO-TRACK</strong>
            </div>
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #2dd4bf;">Hamlib Status</span><br><strong style="color: #34d399;">ONLINE</strong>
            </div>
        </div>
    `;
    const container = document.body.querySelector('.container');
    if (container) container.appendChild(card);
})();
