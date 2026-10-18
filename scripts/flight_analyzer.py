import struct
import os

def analyze_flight_blackbox():
    log_path = "ground_station/flight_blackbox.bin"
    if not os.path.exists(log_path):
        print(f"[ERROR] No se encontró el archivo de caja negra en {log_path}")
        print("Ejecuta primero: python scripts/run_full_mission.py")
        return

    print("=== INICIANDO ANÁLISIS POST-VUELO (CAJA NEGRA) ===")
    
    packet_size = struct.calcsize("<BBIB5fH")
    max_alt = 0.0
    max_vel = 0.0
    max_accel = 0.0
    total_packets = 0

    with open(log_path, "rb") as f:
        while True:
            data = f.read(packet_size)
            if len(data) < packet_size:
                break
            
            header1, header2, timestamp, state, p_baro, p_imu, accel, alt, vel, checksum = struct.unpack("<BBIB5fH", data)
            
            if header1 == 0xAA and header2 == 0x55:
                total_packets += 1
                if alt > max_alt: max_alt = alt
                if vel > max_vel: max_vel = vel
                if accel > max_accel: max_accel = accel

    print(f"\n--- REPORTE TÉCNICO DE MISIÓN FSW v2.0 ---")
    print(f"Paquetes analizados con éxito : {total_packets}")
    print(f"Altitud Máxima (Apogeo EKF)  : {max_alt:.2f} m")
    print(f"Velocidad Pico Registrada    : {max_vel:.2f} m/s")
    print(f"Aceleración Máxima (Boost)   : {max_accel:.2f} Gs")
    print("------------------------------------------")
    print(">>> ANÁLISIS POST-VUELO COMPLETADO CON ÉXITO EXTREMO <<<")

if __name__ == "__main__":
    analyze_flight_blackbox()
