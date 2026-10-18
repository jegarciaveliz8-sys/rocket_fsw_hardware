import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import time

def generar_cohete_avanzado():
    """Genera las geometrías detalladas del cohete."""
    partes = []
    theta = np.linspace(0, 2 * np.pi, 12)
    
    # Cono Nasal
    z_cono = np.linspace(1.2, 1.8, 10)
    theta_grid, z_grid = np.meshgrid(theta, z_cono)
    r_grid = 0.12 * (1.8 - z_grid) / 0.6
    x_cono = r_grid * np.cos(theta_grid)
    y_cono = r_grid * np.sin(theta_grid)
    partes.append((x_cono, y_cono, z_grid, 'crimson', 'Cono', 'wireframe'))

    # Fuselaje Principal
    z_cuerpo = np.linspace(0.0, 1.2, 20)
    theta_grid, z_grid = np.meshgrid(theta, z_cuerpo)
    x_cuerpo = 0.12 * np.cos(theta_grid)
    y_cuerpo = 0.12 * np.sin(theta_grid)
    partes.append((x_cuerpo, y_cuerpo, z_grid, 'gainsboro', 'Fuselaje', 'wireframe'))

    # Aletas
    u = np.linspace(0, 1, 6)
    v = np.linspace(0, 1, 6)
    U, V = np.meshgrid(u, v)
    x_aleta_base = 0.12 + U * 0.18
    z_aleta_base = V * 0.35
    y_aleta_base = np.zeros_like(x_aleta_base)

    for i in range(4):
        angulo = i * np.pi / 2
        x_rot = x_aleta_base * np.cos(angulo) - y_aleta_base * np.sin(angulo)
        y_rot = x_aleta_base * np.sin(angulo) + y_aleta_base * np.cos(angulo)
        z_rot = z_aleta_base
        partes.append((x_rot, y_rot, z_rot, 'darkorange', 'Aletas', 'surface'))

    return partes

def rotar_partes(partes, roll, pitch, yaw, x_offset, y_offset, z_offset):
    r, p, y_ang = np.radians(roll), np.radians(pitch), np.radians(yaw)
    cos_r, sin_r = np.cos(r), np.sin(r)
    cos_p, sin_p = np.cos(p), np.sin(p)
    cos_y, sin_y = np.cos(y_ang), np.sin(y_ang)
    
    partes_trasladadas = []
    for x, y, z, color, nombre, tipo in partes:
        x_flat, y_flat, z_flat = x.flatten(), y.flatten(), z.flatten()
        
        x_rot = cos_y * cos_p * x_flat + (cos_y * sin_p * sin_r - sin_y * cos_r) * y_flat
        y_rot = sin_y * cos_p * x_flat + (sin_y * sin_p * sin_r + cos_y * cos_r) * y_flat
        z_rot = -sin_p * x_flat + cos_p * sin_r * y_flat + cos_p * cos_r * z_flat
        
        x_transl = x_rot.reshape(x.shape) + x_offset
        y_transl = y_rot.reshape(y.shape) + y_offset
        z_transl = z_rot.reshape(z.shape) + z_offset
        
        partes_trasladadas.append((x_transl, y_transl, z_transl, color, nombre, tipo))
        
    return partes_trasladadas

def ejecutar_visualizador_3d():
    fig = plt.figure(figsize=(12, 7))
    ax3d = fig.add_subplot(121, projection='3d')
    ax_gps = fig.add_subplot(122)
    
    cohete_partes = generar_cohete_avanzado()
    print("[INFO] Lanzando Estación Terrena Avanzada con Humo y Mapa GPS...")
    
    lat_base, lon_base = 28.5721, -80.6480
    trayectoria_lat, trayectoria_lon = [], []
    
    try:
        for i in range(100):
            ax3d.clear()
            ax_gps.clear()
            
            if i < 25:
                fase = "PROPULSIÓN (IGNICIÓN)"
                z_pos = i * 15.0
                pitch, roll, yaw = 2.0, 0.0, 0.0
                humo_z = np.linspace(0, z_pos, 15)
                humo_x = np.random.normal(0, 0.05, 15)
                humo_y = np.random.normal(0, 0.05, 15)
            elif i < 60:
                fase = "ASCENSO LIBRE / APOGEO"
                z_pos = 375.0 + (i - 25) * 10.0 - ((i - 25)**2) * 0.3
                pitch = 12.0 + np.sin(i * 0.2) * 4
                roll = i * 2
                yaw = 30.0
                humo_z = np.linspace(z_pos - 100, z_pos, 15)
                humo_x = np.random.normal(0, 0.2, 15)
                humo_y = np.random.normal(0, 0.2, 15)
            else:
                fase = "DESCENSO CON PARACAÍDAS (DERIVA)"
                z_pos = max(0.0, 520.0 - (i - 60) * 13.0)
                pitch = 45.0 + np.sin(i * 0.3) * 15
                roll = (i * 4) % 360
                yaw = 60.0
                humo_z, humo_x, humo_y = [], [], []
                
            lat_actual = lat_base + (i * 0.0001)
            lon_actual = lon_base - (i * 0.00015) if i < 60 else lon_base - (60 * 0.00015) + ((i - 60) * 0.00008)
            trayectoria_lat.append(lat_actual)
            trayectoria_lon.append(lon_actual)
            
            # --- 3D VIEW ---
            ax3d.set_xlim([-3.0, 3.0])
            ax3d.set_ylim([-3.0, 3.0])
            ax3d.set_zlim([0.0, 600.0])
            ax3d.set_title(f"Telemetría 3D | {fase}", fontsize=10, fontweight='bold')
            ax3d.set_xlabel("X (m)")
            ax3d.set_ylabel("Y (m)")
            ax3d.set_zlabel("Altitud (m)")
            
            cohete_rotado = rotar_partes(cohete_partes, roll, pitch, yaw, 0, 0, z_pos)
            for x, y, z, color, nombre, tipo in cohete_rotado:
                if tipo == 'wireframe':
                    ax3d.plot_wireframe(x, y, z, color=color, rstride=3, cstride=3, alpha=0.8)
                else:
                    ax3d.plot_surface(x, y, z, color=color, alpha=0.9, edgecolor='none')
                    
            if len(humo_z) > 0:
                ax3d.scatter(humo_x, humo_y, humo_z, color='lightgray', alpha=0.5, s=40)

            # --- MAPA GPS Y ZONA DE IMPACTO ---
            ax_gps.set_title("Mapa Táctico GPS & Zona de Impacto (Landing Zone)", fontsize=10, fontweight='bold')
            ax_gps.set_xlim(lon_base - 0.008, lon_base + 0.002)
            ax_gps.set_ylim(lat_base - 0.001, lat_base + 0.008)
            ax_gps.set_xlabel("Longitud GPS")
            ax_gps.set_ylabel("Latitud GPS")
            
            ax_gps.scatter([lon_base], [lat_base], color='green', s=100, marker='^', label='Rampa (Pad LC-39)')
            ax_gps.plot(trayectoria_lon, trayectoria_lat, color='dodgerblue', linewidth=2.5, label='Ruta Histórica GPS')
            ax_gps.scatter([lon_actual], [lat_actual], color='red', s=120, marker='o', label='Posición Actual Cohete')
            
            lz_lat, lz_lon = lat_base + 0.0065, lon_base - 0.0025
            ax_gps.scatter([lz_lon], [lz_lat], color='darkorange', s=150, marker='X', label='Zona de Impacto (LZ-1)')
            
            ax_gps.legend(loc='upper right', fontsize=8)
            ax_gps.grid(True, linestyle='--', alpha=0.5)
            
            plt.tight_layout()
            plt.draw()
            plt.pause(0.05)
            
    except KeyboardInterrupt:
        print("\n[INFO] Visualizador cerrado.")

if __name__ == "__main__":
    ejecutar_visualizador_3d()
