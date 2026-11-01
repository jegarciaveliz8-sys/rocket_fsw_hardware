const map = L.map('map', { maxZoom: 20 }).setView([14.7883, -90.1988], 15);
const layers = {
    roadmap: L.tileLayer('https://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', { maxZoom: 20, subdomains: ['mt0', 'mt1', 'mt2', 'mt3'] }),
    satellite: L.tileLayer('https://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', { maxZoom: 20, subdomains: ['mt0', 'mt1', 'mt2', 'mt3'] }),
    hybrid: L.tileLayer('https://{s}.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', { maxZoom: 20, subdomains: ['mt0', 'mt1', 'mt2', 'mt3'] })
};
let activeLayer = layers.hybrid.addTo(map);

function setLayer(name) {
    if (layers[name]) {
        map.removeLayer(activeLayer);
        activeLayer = layers[name].addTo(map);
    }
}
function locateUser() { map.setView([14.7883, -90.1988], 16); }

const droneIcon = L.divIcon({
    className: 'custom-drone',
    html: '<div style="width:16px; height:16px; background:#ef4444; border:2px solid #fff; border-radius:50%; box-shadow:0 0 10px #ef4444;"></div>',
    iconSize: [16, 16], iconAnchor: [8, 8]
});
const droneMarker = L.marker([14.7883, -90.1988], { icon: droneIcon }).addTo(map).bindPopup("<b>ODYSSEY-1 Sanarate Base</b>");
const trajectoryPath = L.polyline([], { color: '#38bdf8', weight: 4, opacity: 0.85 }).addTo(map);

let dynamicWaypoints = [];
let waypointMarkers = [];

map.on('click', async function(e) {
    const lat = e.latlng.lat;
    const lon = e.latlng.lng;
    const wpData = { 
        lat: lat, 
        lon: lon, 
        alt: 35.0, 
        loiter: 5, // 5 segundos por defecto para tomar fotos
        name: `WP Sanarate #${dynamicWaypoints.length + 1}` 
    };
    
    dynamicWaypoints.push(wpData);
    
    const marker = L.circleMarker([lat, lon], { radius: 6, color: '#facc15', fillColor: '#facc15', fillOpacity: 0.9 }).addTo(map)
     .bindPopup(`<b>${wpData.name}</b><br>Lat: ${lat.toFixed(4)}<br>Lon: ${lon.toFixed(4)}<br>Loiter: ${wpData.loiter}s [📸]`);
    waypointMarkers.push(marker);

    renderWaypointsTable();
    logConsole(`[MAPA] Waypoint con cámara añadido: ${wpData.name} (Loiter: ${wpData.loiter}s)`);
});

function renderWaypointsTable() {
    const tbody = document.getElementById("waypoints-table-body");
    if (!tbody) return;
    
    if (dynamicWaypoints.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4" style="text-align:center; color:#8b949e; padding:10px;">Haz clic en el mapa para añadir puntos.</td></tr>`;
        return;
    }

    let html = "";
    dynamicWaypoints.forEach((wp, i) => {
        html += `
            <tr>
                <td><b>WP${i}</b></td>
                <td style="font-family:monospace; font-size:10px;">${wp.lat.toFixed(3)},<br>${wp.lon.toFixed(3)}</td>
                <td><input type="number" value="${wp.alt}" onchange="updateWaypointParam(${i}, 'alt', this.value)" style="width:45px;"></td>
                <td><input type="number" value="${wp.loiter || 0}" onchange="updateWaypointParam(${i}, 'loiter', this.value)" style="width:35px;" title="Segundos de Loiter / Foto">s</td>
                <td><button onclick="removeWaypoint(${i})" style="background:#da3633; color:#fff; border:none; padding:2px 6px; border-radius:3px; cursor:pointer;">X</button></td>
            </tr>
        `;
    });
    tbody.innerHTML = html;
}

function updateWaypointParam(index, field, value) {
    if (dynamicWaypoints[index]) {
        dynamicWaypoints[index][field] = parseFloat(value) || 0.0;
        logConsole(`[PLANIFICADOR] WP${index} ${field} actualizado a ${value}`);
    }
}

function removeWaypoint(index) {
    if (waypointMarkers[index]) {
        map.removeLayer(waypointMarkers[index]);
        waypointMarkers.splice(index, 1);
    }
    dynamicWaypoints.splice(index, 1);
    renderWaypointsTable();
    logConsole(`[PLANIFICADOR] Waypoint #${index} eliminado.`);
}

function clearMissionPath() {
    waypointMarkers.forEach(marker => map.removeLayer(marker));
    waypointMarkers = [];
    dynamicWaypoints = [];
    renderWaypointsTable();
    logConsole("[MAPA] Todos los waypoints fueron limpiados.");
}
