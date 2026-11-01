let telemetryChart = null;

window.addEventListener('DOMContentLoaded', () => {
    const ctx = document.getElementById('telemetryChart').getContext('2d');
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
                    yAxisID: 'y',
                    tension: 0.2
                },
                {
                    label: 'Velocidad (m/s)',
                    data: [],
                    borderColor: '#38bdf8',
                    borderWidth: 1.5,
                    yAxisID: 'y1',
                    tension: 0.2
                },
                {
                    label: 'Deriva Enlace (ms)',
                    data: [],
                    borderColor: '#facc15',
                    borderWidth: 1,
                    yAxisID: 'y2',
                    tension: 0.1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: false,
            scales: {
                x: { ticks: { color: '#8b949e', font: { size: 10 } }, grid: { color: '#21262d' } },
                y: { type: 'linear', display: true, position: 'left', ticks: { color: '#34d399', font: { size: 10 } }, grid: { color: '#21262d' } },
                y1: { type: 'linear', display: true, position: 'right', ticks: { color: '#38bdf8', font: { size: 10 } }, grid: { drawOnChartArea: false } },
                y2: { type: 'linear', display: false, position: 'right', min: 0, max: 1 }
            },
            plugins: { legend: { labels: { color: '#c9d1d9', font: { size: 10 } } } }
        }
    });
});

function updateChartData(time, alt, speed, drift = 0.15) {
    if (!telemetryChart) return;
    
    if (telemetryChart.data.labels.length > 20) {
        telemetryChart.data.labels.shift();
        telemetryChart.data.datasets[0].data.shift();
        telemetryChart.data.datasets[1].data.shift();
        telemetryChart.data.datasets[2].data.shift();
    }
    
    telemetryChart.data.labels.push(`T+${time}s`);
    telemetryChart.data.datasets[0].data.push(alt);
    telemetryChart.data.datasets[1].data.push(speed);
    telemetryChart.data.datasets[2].data.push(drift);
    
    telemetryChart.update();
}
