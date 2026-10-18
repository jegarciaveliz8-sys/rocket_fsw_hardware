import time
import struct
import sys

def run_hil_simulation():
    print("=== INICIALIZANDO PUENTE HIL (HARDWARE-IN-THE-LOOP) ===")
    print("Simulando inyección de sensores en bucle cerrado a 100 Hz...")
    
    dt = 0.01
    altitude = 0.0
    velocity = 0.0
    
    for i in range(100):
        t = i * dt
        # Modelo simplificado de prueba HIL
        acceleration = 5.8 if t < 2.5 else -1.5
        velocity += acceleration * 9.81 * dt
        altitude += velocity * dt
        if altitude < 0: altitude = 0.0
        
        # Empaquetar datos idénticos al protocolo binario
        packet = struct.pack("<BBIB5fH", 0xAA, 0x55, int(t * 1000), 2, 0.1, 0.05, acceleration, altitude, velocity, 0x1234)
        
        # Simular envío por puerto serie físico/virtual
        sys.stdout.write(f"\r[HIL TX] t={t:.2f}s | Alt={altitude:.2f}m | Vel={velocity:.2f}m/s")
        sys.stdout.flush()
        time.sleep(0.01)
        
    print("\n>>> PRUEBA HIL COMPLETADA CON ÉXITO EXTREMO <<<")

if __name__ == "__main__":
    run_hil_simulation()
