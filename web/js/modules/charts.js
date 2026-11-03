// --- SUBSISTEMA DE TELEMETRÍA GRÁFICA (Chart.js) ---
let telemetryChartInstance = null;
const maxDataPoints = 30;

function initTelemetryChart() {
    const ctx = document.getElementById("telemetryChart");
    if (!ctx) return;

    telemetryChartInstance = new Chart(ctx, {
        type: "line",
        data: {
            labels: [],
            datasets: [
                {
                    label: "Altitud (m)",
                    data: [],
                    borderColor: "#38bdf8",
                    backgroundColor: "rgba(56, 189, 248, 0.1)",
                    borderWidth: 2,
                    yAxisID: "y",
                    tension: 0.2
                },
                {
                    label: "Batería (%)",
                    data: [],
                    borderColor: "#34d399",
                    backgroundColor: "rgba(52, 211, 153, 0.1)",
                    borderWidth: 2,
                    yAxisID: "y1",
                    tension: 0.2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    ticks: { color: "#8b949e", font: { size: 9 } },
                    grid: { color: "#30363d" }
                },
                y: {
                    type: "linear",
                    display: true,
                    position: "left",
                    ticks: { color: "#38bdf8", font: { size: 9 } },
                    grid: { color: "#30363d" }
                },
                y1: {
                    type: "linear",
                    display: true,
                    position: "right",
                    ticks: { color: "#34d399", font: { size: 9 } },
                    grid: { drawOnChartArea: false }
                }
            },
            plugins: {
                legend: { labels: { color: "#c9d1d9", font: { size: 10 } } }
            }
        }
    });
}

function updateTelemetryChart(time, altitude, battery) {
    if (!telemetryChartInstance) return;
    const timeLabel = `T+${time}s`;
    telemetryChartInstance.data.labels.push(timeLabel);
    telemetryChartInstance.data.datasets[0].data.push(altitude);
    telemetryChartInstance.data.datasets[1].data.push(battery);

    if (telemetryChartInstance.data.labels.length > maxDataPoints) {
        telemetryChartInstance.data.labels.shift();
        telemetryChartInstance.data.datasets[0].data.shift();
        telemetryChartInstance.data.datasets[1].data.shift();
    }
    telemetryChartInstance.update("none");
}
