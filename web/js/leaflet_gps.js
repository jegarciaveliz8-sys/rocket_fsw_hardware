const map = L.map('map').setView([28.5721, -80.6480], 3);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { 
    maxZoom: 18,
    attribution: '© OpenStreetMap | ODYSSEY-1 GPS Tracking'
}).addTo(map);

const rocketMarker = L.marker([28.5721, -80.6480]).addTo(map)
    .bindPopup("<b>ODYSSEY-1 GCS</b><br>Rastreo GPS Orbital Activo");

let gpsTrailPoints = [];
const trajectoryLine = L.polyline([], { color: '#38bdf8', weight: 3, opacity: 0.8 }).addTo(map);

const dsnStations = {
    "Cape Canaveral": [28.5721, -80.6480],
    "Madrid DSN": [40.4262, -4.2497],
    "Goldstone DSN": [35.4266, -116.8900],
    "Canberra DSN": [-35.4014, 148.9817]
};
for (let name in dsnStations) {
    L.circle(dsnStations[name], { radius: 800000, color: '#34d399', fillColor: '#34d399', fillOpacity: 0.15 })
        .addTo(map)
        .bindPopup(`<b>Estación DSN:</b> ${name}`);
}

function updateGPSPosition(lat, lon) {
    let currentLat = lat !== undefined ? lat : 28.5721;
    let currentLon = lon !== undefined ? lon : -80.6480;
    const newLatLng = [currentLat, currentLon];

    rocketMarker.setLatLng(newLatLng);
    gpsTrailPoints.push(newLatLng);
    if (gpsTrailPoints.length > 100) gpsTrailPoints.shift();
    trajectoryLine.setLatLngs(gpsTrailPoints);
    map.panTo(newLatLng, { animate: true });
}
