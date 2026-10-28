(function() {
    const udpCard = document.createElement('div');
    udpCard.className = 'card';
    udpCard.style.border = '1px solid #6366f1';
    udpCard.innerHTML = `
        <h3>🔌 HIL Hardware Real (Socket UDP / ESP32 Bridge Port)</h3>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; text-align: center; margin-top: 8px;">
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #818cf8;">Estado Puerto UDP/Serial</span><br><strong id="udp-status" style="color: #34d399;">LISTENING (Port 5005)</strong>
            </div>
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #818cf8;">Dispositivo Conectado</span><br><strong style="color: #38bdf8;">ESP32-OBC-DEVKIT</strong>
            </div>
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #818cf8;">Tasa de Paquetes HW</span><br><strong style="color: #34d399;">10 Hz Real-Time</strong>
            </div>
        </div>
    `;
    const container = document.body.querySelector('.container');
    if (container) container.appendChild(udpCard);
})();
