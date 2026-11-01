// --- Módulo de Horizonte Artificial (PFD Attitude Indicator) ---

function drawAttitudeIndicator(pitch = 0, roll = 0, yaw = 0) {
    const canvas = document.getElementById('attitudeCanvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    
    const width = canvas.width = canvas.clientWidth;
    const height = canvas.height = canvas.clientHeight;
    const cx = width / 2;
    const cy = height / 2;

    ctx.clearRect(0, 0, width, height);

    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate((roll * Math.PI) / 180);

    // Desplazamiento vertical por el ángulo de Pitch
    const pitchOffset = pitch * 3;

    // Fondo Cielo
    ctx.fillStyle = '#0284c7';
    ctx.fillRect(-width, -height * 2 + pitchOffset, width * 2, height * 2);

    // Fondo Tierra
    ctx.fillStyle = '#b45309';
    ctx.fillRect(-width, pitchOffset, width * 2, height * 2);

    // Línea de horizonte
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(-width, pitchOffset);
    ctx.lineTo(width, pitchOffset);
    ctx.stroke();

    ctx.restore();

    // Retícula fija central del avión
    ctx.strokeStyle = '#34d399';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(cx - 20, cy); ctx.lineTo(cx - 8, cy);
    ctx.moveTo(cx + 8, cy); ctx.lineTo(cx + 20, cy);
    ctx.moveTo(cx, cy - 8); ctx.lineTo(cx, cy - 2);
    ctx.stroke();
}

window.addEventListener('DOMContentLoaded', () => {
    drawAttitudeIndicator(0, 0, 0);
});
