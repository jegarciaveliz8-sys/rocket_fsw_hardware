// --- MÓDULO GIS AVANZADO & GEOLOCALIZACIÓN (ODYSSEY-1 Sanarate) ---

const map = L.map('map', { maxZoom: 20, fullscreenControl: true }).setView([14.7883, -90.1988], 15);

// Capas de Google Maps configurables
const layers = {
    roadmap: L.tileLayer('https://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', { maxZoom: 20, subdomains: ['mt0', 'mt1', 'mt2', 'mt3'], attribution: '&copy; Google Maps' }),
    satellite: L.tileLayer('https://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', { maxZoom: 20, subdomains: ['mt0', 'mt1', 'mt2', 'mt3'], attribution: '&copy; Google Maps' }),
    hybrid: L.tileLayer('https://{s}.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', { maxZoom: 20, subdomains: ['mt0', 'mt1', 'mt2', 'mt3'], attribution: '&copy; Google Maps' })
};

let activeLayer = layers.hybrid.addTo(map);

function setLayer(layerName) {
    if (layers[layerName]) {
        map.removeLayer(activeLayer);
        activeLayer = layers[layerName].addTo(map);
    }
}

// Marcador del Vehículo (Dron F450) en Sanarate
const rocketIcon = L.divIcon({
    className: 'custom-radar-marker',
    html: '<div style="width:16px; height:16px; background:#ef4444; border:2px solid #ffffff; border-radius:50%; box-shadow: 0 0 14px #ef4444;"></div>',
    iconSize: [16, 16],
    iconAnchor: [8, 8]
});
const rocketMarker = L.marker([14.7883, -90.1988], { icon: rocketIcon }).addTo(map).bindPopup("<b>ODYSSEY-1 Vehicle (Sanarate Base)</b>");
const trajectoryPath = L.polyline([], { color: '#38bdf8', weight: 4, opacity: 0.85 }).addTo(map);

let userMarker = null;
let userCircle = null;
let dynamicWaypoints = [];

function locateUser() {
    if (!navigator.geolocation) {
        alert("La geolocalización no es compatible con tu navegador.");
        return;
    }
    
    const options = { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 };

    navigator.geolocation.getCurrentPosition(
        (position) => {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            const accuracy = position.coords.accuracy;
            updateUserPositionOnMap(lat, lon, accuracy, "Geolocalización GPS Directa");
        },
        (error) => {
            console.warn("Error de geolocalización por hardware:", error.message);
            updateUserPositionOnMap(14.7883, -90.1988, 500, "Fallback Estación Sanarate");
        },
        options
    );
}

function updateUserPositionOnMap(lat, lon, accuracy, sourceDesc) {
    const userIcon = L.divIcon({
        className: 'user-gps-marker',
        html: '<div style="width:14px; height:14px; background:#34d399; border:2px solid #ffffff; border-radius:50%; box-shadow: 0 0 10px #34d399;"></div>',
        iconSize: [14, 14],
        iconAnchor: [7, 7]
    });

    if (userMarker) {
        userMarker.setLatLng([lat, lon]);
        userCircle.setLatLng([lat, lon]);
        userCircle.setRadius(accuracy);
    } else {
        userMarker = L.marker([lat, lon], { icon: userIcon }).addTo(map).bindPopup(`<b>📍 Estación Terrena</b><br>Lat: ${lat.toFixed(4)}<br>Lon: ${lon.toFixed(4)}`).openPopup();
        userCircle = L.circle([lat, lon], { radius: accuracy, color: '#34d399', fillColor: '#34d399', fillOpacity: 0.15 }).addTo(map);
    }
    map.setView([lat, lon], 14);
}

// --- INTERACTIVIDAD: CLIC EN EL MAPA CREA UN WAYPOINT DINÁMICO ---
map.on('click', function(e) {
    const lat = e.latlng.lat;
    const lon = e.latlng.lng;
    const wpData = { lat: lat, lon: lon, alt: 35.0, name: `WP Sanarate #${dynamicWaypoints.length + 1}` };
    
    dynamicWaypoints.push(wpData);
    renderWaypointsList();

    L.circleMarker([lat, lon], {
        radius: 6,
        color: '#facc15',
        fillColor: '#facc15',
        fillOpacity: 0.9
    }).addTo(map).bindPopup(`<b>${wpData.name}</b><br>Lat: ${lat.toFixed(4)}<br>Lon: ${lon.toFixed(4)}`);

    const consoleBox = document.getElementById("mcc-console");
    if(consoleBox) {
        consoleBox.innerHTML += `<br>[MAPA] Waypoint añadido: ${wpData.name} (${lat.toFixed(4)}, ${lon.toFixed(4)})`;
        consoleBox.scrollTop = consoleBox.scrollHeight;
    }
});

function renderWaypointsList() {
    const container = document.getElementById("waypoints-list-container");
    if (!container) return;
    
    if (dynamicWaypoints.length === 0) {
        container.innerHTML = "No hay waypoints dinámicos creados.";
        return;
    }

    let html = "";
    dynamicWaypoints.forEach((wp, index) => {
        html += `<div><b>WP${index}:</b> ${wp.lat.toFixed(4)}, ${wp.lon.toFixed(4)} (${wp.alt}m)</div>`;
    });
    container.innerHTML = html;
}

async function saveCurrentMission() {
    if (dynamicWaypoints.length === 0) {
        alert("No hay waypoints para guardar.");
        return;
    }

    try {
        const response = await fetch('/api/mission-planner/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ waypoints: dynamicWaypoints })
        });
        const result = await response.json();
        alert(result.message || "Misión guardada con éxito en el servidor.");
    } catch (err) {
        console.error("Error al guardar la misión", err);
    }
}

async function loadSavedMission() {
    try {
        const response = await fetch('/api/mission-planner/load');
        const result = await response.json();
        
        if (result.status === "SUCCESS" && result.waypoints) {
            dynamicWaypoints = result.waypoints;
            renderWaypointsList();
            
            dynamicWaypoints.forEach(wp => {
                L.circleMarker([wp.lat, wp.lon], {
                    radius: 6,
                    color: '#38bdf8',
                    fillColor: '#38bdf8',
                    fillOpacity: 0.9
                }).addTo(map);
            });
            alert(`Misión cargada correctamente (${dynamicWaypoints.length} waypoints).`);
        } else {
            alert(result.message || "No se encontró ninguna misión guardada.");
        }
    } catch (err) {
        console.error("Error al cargar la misión", err);
    }
}

function clearMissionPath() {
    dynamicWaypoints = [];
    renderWaypointsList();
    alert("Lista de waypoints limpiada.");
}

// Función para actualizar la posición en tiempo real desde el WebSocket
window.updateGPSPosition = function(lat, lon) {
    if (lat !== undefined && lon !== undefined) {
        const newPos = [lat, lon];
        rocketMarker.setLatLng(newPos);
        trajectoryPath.addLatLng(newPos);
        
        const latEl = document.getElementById("gps-lat");
        const lonEl = document.getElementById("gps-lon");
        if(latEl) latEl.innerText = lat.toFixed(4) + "°";
        if(lonEl) lonEl.innerText = lon.toFixed(4) + "°";
    }
};

window.updateMapPosition = window.updateGPSPosition;
