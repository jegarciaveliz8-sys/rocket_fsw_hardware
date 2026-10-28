(function() {
    const container = document.createElement('div');
    container.className = 'card';
    container.style.border = '1px solid #f59e0b';
    container.innerHTML = `
        <h3>⚙️ Aviónica HIL & Ruedas de Reacción (RPM Actuadores)</h3>
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; text-align: center; margin-top: 8px;">
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #94a3b8;">RW-1 (X)</span><br><strong id="rw1-rpm" style="color: #38bdf8;">+4200 RPM</strong>
            </div>
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #94a3b8;">RW-2 (Y)</span><br><strong id="rw2-rpm" style="color: #38bdf8;">-1850 RPM</strong>
            </div>
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #94a3b8;">RW-3 (Z)</span><br><strong id="rw3-rpm" style="color: #38bdf8;">+910 RPM</strong>
            </div>
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #94a3b8;">Deriva IMU</span><br><strong id="imu-bias" style="color: #34d399;">0.002°/s</strong>
            </div>
        </div>
    `;
    document.body.querySelector('.container').appendChild(container);
})();
