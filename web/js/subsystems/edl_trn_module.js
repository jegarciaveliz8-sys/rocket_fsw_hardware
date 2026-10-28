(function() {
    const edlCard = document.createElement('div');
    edlCard.className = 'card';
    edlCard.style.border = '1px solid #f97316';
    edlCard.innerHTML = `
        <h3>🛸 EDL & TRN (Entry, Descent, Landing & Terrain Navigation)</h3>
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; text-align: center; margin-top: 8px;">
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #fb923c;">Radar Altimetría Láser</span><br><strong style="color: #38bdf8;">12,450 metros</strong>
            </div>
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #fb923c;">Correlación TRN Map</span><br><strong style="color: #34d399;">MATCHED (Error < 1.2m)</strong>
            </div>
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #fb923c;">Velocidad Vertical</span><br><strong style="color: #f87171;">-45.2 m/s</strong>
            </div>
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #fb923c;">Despliegue Paracaídas</span><br><strong style="color: #facc15;">ARMED (Mach 1.5)</strong>
            </div>
        </div>
    `;
    const container = document.body.querySelector('.container');
    if (container) container.appendChild(edlCard);
})();
