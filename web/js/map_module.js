// --- MÓDULO GIS AVANZADO & GEOLOCALIZACIÓN (ODYSSEY-1) ---
const map = L.map('map', { maxZoom: 20, fullscreenControl: true }).setView([28.5721, -80.6480], 16);

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

// Marcador del Cohete
const rocketIcon = L.divIcon({
    className: 'custom-radar-marker',
    html: '<div style="width:16px; height:16px; background:#ef4444; border:2px solid #ffffff; border-radius:50%; box-shadow: 0 0 14px #ef4444;"></div>',
    iconSize: [16, 16],
    iconAnchor: [8, 8]
});
const rocketMarker = L.marker([28.5721, -80.6480], { icon: rocketIcon }).addTo(map).bindPopup("<b>ODYSSEY-1 Vehicle</b>");
const trajectoryPath = L.polyline([], { color: '#38bdf8', weight: 4, opacity: 0.85 }).addTo(map);

let userMarker = null;
let userCircle = null;

function locateUser() {
    if (!navigator.geolocation) {
        alert("La geolocalización no es compatible con tu navegador.");
        return;
    }
    
    // Opciones estrictas para evitar triangulaciones erróneas por IP
    const options = {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0
    };

    navigator.geolocation.getCurrentPosition(
        (position) => {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            const accuracy = position.coords.accuracy;

            updateUserPositionOnMap(lat, lon, accuracy, "Geolocalización GPS Directa");
        },
        (error) => {
            console.warn("Error de geolocalización por hardware:", error.message);
            // Fallback inteligente a Sanarate, El Progreso si falla la red
            const fallbackLat = 14.7797;
            const fallbackLon = -90.1136;
            updateUserPositionOnMap(fallbackLat, fallbackLon, 500, "Fallback Manual (Sanarate, El Progreso)");
            alert("El navegador devolvió una ubicación errónea (Cobán). Se ha fijado la estación terrena en Sanarate, El Progreso. Haz clic en el mapa para ajustar si es necesario.");
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
        userMarker = L.marker([lat, lon], { icon: userIcon }).addTo(map).bindPopup(`<b>📍 Estación Terrena</b><br>Lat: ${lat.toFixed(4)}<br>Lon: ${lon.toFixed(4)}<br><small>(${sourceDesc})</small>`).openPopup();
        userCircle = L.circle([lat, lon], { radius: accuracy, color: '#34d399', fillColor: '#34d399', fillOpacity: 0.15 }).addTo(map);
    }

    map.setView([lat, lon], 14);
    document.getElementById("mcc-console").innerHTML += `<br>[GPS] Estación terrena fijada en: ${lat.toFixed(4)}°, ${lon.toFixed(4)}° (${sourceDesc})`;
}

// Permite hacer clic en el mapa para corregir/fijar la ubicación manualmente si se desea
map.on('click', function(e) {
    const lat = e.latlng.lat;
    const lon = e.latlng.lng;
    updateUserPositionOnMap(lat, lon, 100, "Selección Manual en Mapa");
});

window.updateGPSPosition = function(lat, lon) {
    if (lat !== undefined && lon !== undefined) {
        const newPos = [lat, lon];
        rocketMarker.setLatLng(newPos);
        trajectoryPath.addLatLng(newPos);
        document.getElementById("gps-lat").innerText = lat.toFixed(4) + "°";
        document.getElementById("gps-lon").innerText = lon.toFixed(4) + "°";
    }
};
