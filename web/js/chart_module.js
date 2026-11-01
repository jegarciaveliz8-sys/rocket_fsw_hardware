// --- Módulo de Gráficas de Telemetría en Tiempo Real (Chart.js) ---

let telemetryChart = null;

function initTelemetryChart() {
    const canvas = document.getElementById('telemetryChart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    telemetryChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Altitud (m)',
                    data: [],
                    borderColor: '#34d399',
                    backgroundColor: 'rgba(52, 211, 153, 0.1)',
                    borderWidth: 2,
                    tension: 0.2,
                    yAxisID: 'y'
                },
                {
                    label: 'Velocidad (m/s)',
                    data: [],
                    borderColor: '#38bdf8',
                    backgroundColor: 'rgba(56, 189, 248, 0.1)',
                    borderWidth: 2,
                    tension: 0.2,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: false, // Desactivar animación para máxima fluidez en streaming
            scales: {
                x: {
                    grid: { color: '#21262d' },
                    ticks: { color: '#8b949e', font: { family: 'monospace', size: 10 } }
                },
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    grid: { color: '#21262d' },
                    ticks: { color: '#34d399', font: { family: 'monospace', size: 10 } }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    grid: { drawOnChartArea: false },
                    ticks: { color: '#38bdf8', font: { family: 'monospace', size: 10 } }
                }
            },
            plugins: {
                legend: { 
                    labels: { color: '#c9d1d9', font: { family: 'monospace', size: 11 } } 
                }
            }
        }
    });
}

function updateChartData(timeLabel, altitude, velocity) {
    if (!telemetryChart) return;
    
    // Mantener una ventana deslizante de los últimos 20 puntos de telemetría
    if (telemetryChart.data.labels.length > 20) {
        telemetryChart.data.labels.shift();
        telemetryChart.data.datasets[0].data.shift();
        telemetryChart.data.datasets[1].data.shift();
    }

    telemetryChart.data.labels.push(`T+${timeLabel}s`);
    telemetryChart.data.datasets[0].data.push(altitude);
    telemetryChart.data.datasets[1].data.push(velocity);
    telemetryChart.update();
}

window.addEventListener('DOMContentLoaded', () => {
    initTelemetryChart();
});
