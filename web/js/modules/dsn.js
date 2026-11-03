// --- SUBSISTEMA RED DSN GLOBAL CON REORIENTACIÓN DE MAPA ---
const DSN_COORDS = {
    "DSS-63": { name: "Madrid (DSS-63)", lat: 40.4295, lon: -4.2458 },
    "DSS-14": { name: "Goldstone (DSS-14)", lat: 35.4267, lon: -116.8890 },
    "DSS-43": { name: "Canberra (DSS-43)", lat: -35.4014, lon: 148.9817 }
};

let dsnMarker = null;

async function switchDSNStation(stationName) {
    try {
        let res = await fetch("/api/dsn/switch", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ station: stationName })
        });
        let data = await res.json();
        
        const labelName = document.getElementById("lbl-active-dsn-name");
        if (labelName) {
            labelName.innerText = `📡 RED DSN: ${data.name || stationName} [Global Link]`;
        }

        const targetCoords = DSN_COORDS[stationName] || { lat: data.lat, lon: data.lon, name: data.name };
        
        // Buscar la instancia activa del mapa en el window global
        const activeMap = window.map || window.leafletMap || (typeof map !== 'undefined' ? map : null);

        if (activeMap && targetCoords.lat && targetCoords.lon) {
            activeMap.flyTo([targetCoords.lat, targetCoords.lon], 6, { duration: 1.5 });

            if (!dsnMarker) {
                dsnMarker = L.marker([targetCoords.lat, targetCoords.lon]).addTo(activeMap);
            } else {
                dsnMarker.setLatLng([targetCoords.lat, targetCoords.lon]);
            }
            dsnMarker.bindPopup(`<b>Estación Terrena DSN</b><br>${targetCoords.name}`).openPopup();

            const radarCoords = document.getElementById("radar-coords");
            if (radarCoords) {
                radarCoords.innerText = `LAT: ${targetCoords.lat.toFixed(4)}° | LON: ${targetCoords.lon.toFixed(4)}°`;
            }
        }

        if (typeof logToConsole === "function") {
            logToConsole(`[DSN BROKER] Estación activa conmutada a: ${stationName}`);
        }
    } catch (e) {
        console.error("[DSN ERROR] Error al conmutar estación:", e);
    }
}
