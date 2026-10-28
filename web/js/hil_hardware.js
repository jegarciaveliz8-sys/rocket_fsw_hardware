// --- Subsistema HIL (Hardware-in-the-Loop) y Actuadores ---
const hilContainer = document.createElement('div');
hilContainer.className = 'card';
hilContainer.style.border = '1px solid #f59e0b';
hilContainer.innerHTML = `
    <h3>⚙️ Aviónica HIL & Ruedas de Reacción (RPM Actuadores)</h3>
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; text-align: center; margin-top: 8px;">
        <div style="background: #020617; padding: 8px; border-radius: 4px;">
            <span style="font-size: 11px; color: #94a3b8;">Rueda X (RW-1)</span><br>
            <strong id="rw1-rpm" style="color: #38bdf8;">+4200 RPM</strong>
        </div>
        <div style="background: #020617; padding: 8px; border-radius: 4px;">
            <span style="font-size: 11px; color: #94a3b8;">Rueda Y (RW-2)</span><br>
            <strong id="rw2-rpm" style="color: #38bdf8;">-1850 RPM</strong>
        </div>
        <div style="background: #020617; padding: 8px; border-radius: 4px;">
            <span style="font-size: 11px; color: #94a3b8;">Rueda Z (RW-3)</span><br>
            <strong id="rw3-rpm" style="color: #38bdf8;">+910 RPM</strong>
        </div>
        <div style="background: #020617; padding: 8px; border-radius: 4px;">
            <span style="font-size: 11px; color: #94a3b8;">Deriva IMU (Bias)</span><br>
            <strong id="imu-bias" style="color: #34d399;">0.002 deg/s</strong>
        </div>
    </div>
`;

// Insertarlo antes de la gráfica en el contenedor principal
document.addEventListener("DOMContentLoaded", () => {
    const chartCard = document.querySelector('.chart-container').closest('.card');
    chartCard.parentNode.insertBefore(hilContainer, chartCard);
});

// Actualizar valores HIL con el WebSocket existente
function updateHILTelemetry(time) {
    const rw1 = document.getElementById("rw1-rpm");
    const rw2 = document.getElementById("rw2-rpm");
    const rw3 = document.getElementById("rw3-rpm");
    if (rw1 && rw2 && rw3) {
        rw1.innerText = (4200 + Math.sin(time * 0.2) * 150).toFixed(0) + " RPM";
        rw2.innerText = (-1850 + Math.cos(time * 0.15) * 100).toFixed(0) + " RPM";
        rw3.innerText = (910 + Math.sin(time * 0.3) * 50).toFixed(0) + " RPM";
    }
}
