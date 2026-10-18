import time
import json
import os
import math
import pty

def run_hil_simulation():
    # Crear un par de puertos serie virtuales en Linux (master/slave)
    master, slave = pty.openpty()
    s_name = os.ttyname(slave)
    
    # Crear enlace simbólico para la app
    symlink_path = "/tmp/ttyV0"
    if os.path.exists(symlink_path):
        os.remove(symlink_path)
    os.symlink(s_name, symlink_path)
    
    print(f"📡 SIMULADOR HIL ACTIVO. Puerto serie creado en: {symlink_path}")
    print("Enviando telemetría simulada desde microcontrolador virtual...")
    
    t = 0
    alt = 0.0
    vel = 0.0
    
    try:
        while True:
            t += 1
            alt += 0.35 + (t * 0.002)
            vel += 55.0 + (t * 0.4)
            
            packet = {
                "time": t,
                "altitude": round(alt, 2),
                "velocity": round(vel, 1),
                "pitch": round(max(0.0, 90.0 - (t * 0.8)), 1),
                "status": "HIL_FLIGHT_ACTIVE"
            }
            
            raw_data = json.dumps(packet) + "\n"
            os.write(master, raw_data.encode('utf-8'))
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("Simulador HIL detenido.")

if __name__ == "__main__":
    run_hil_simulation()
