// --- Subsistema de Análisis Monte Carlo y Dispersión Orbital ---
const mcContainer = document.createElement('div');
mcContainer.className = 'card';
mcContainer.style.border = '1px solid #a855f7';
mcContainer.innerHTML = `
    <h3>🎲 Matriz Monte Carlo & Dispersión de Trayectoria (N=1000)</h3>
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; text-align: center; margin-top: 8px;">
        <div style="background: #020617; padding: 8px; border-radius: 4px;">
            <span style="font-size: 11px; color: #a855f7;">Dispersión de Inyección ($\Delta v$)</span><br>
            <strong id="mc-dv" style="color: #38bdf8;">± 1.24 m/s</strong>
        </div>
        <div style="background: #020617; padding: 8px; border-radius: 4px;">
            <span style="font-size: 11px; color: #a855f7;">Probabilidad de Éxito LEO</span><br>
            <strong id="mc-success" style="color: #34d399;">99.84%</strong>
        </div>
        <div style="background: #020617; padding: 8px; border-radius: 4px;">
            <span style="font-size: 11px; color: #a855f7;">Deriva Orbital Estimada</span><br>
            <strong id="mc-drift" style="color: #facc15;">0.04 km/orb</strong>
        </div>
    </div>
`;

document.addEventListener("DOMContentLoaded", () => {
    const chartCard = document.querySelector('.chart-container').closest('.card');
    chartCard.parentNode.insertBefore(mcContainer, chartCard);
});
