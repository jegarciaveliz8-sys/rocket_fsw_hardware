import os
import time
import numpy as np

class ComputadoraDeVuelo:
    def __init__(self):
        # Estados de la misión
        self.estado = "PRE_LANZAMIENTO"
        self.altitud = 0.0
        self.velocidad = 0.0
        self.altitud_maxima = 0.0
        
        # Archivo de Caja Negra (Black Box)
        os.makedirs("data", exist_ok=True)
        self.log_filename = "data/black_box_flight.csv"
        self.log_file = open(self.log_filename, "w")
        self.log_file.write("tiempo,estado,altitud,velocidad,evento\n")
        
    def actualizar_fsm(self, tiempo, altitud, velocidad):
        self.altitud = altitud
        self.velocidad = velocidad
        
        if altitud > self.altitud_maxima:
            self.altitud_maxima = altitud
            
        evento = "NINGUNO"
        
        # Lógica de Transición de Estados (FSM)
        if self.estado == "PRE_LANZAMIENTO" and altitud > 2.0:
            self.estado = "PROPULSION"
            evento = "IGNICION_MOTOR"
            
        elif self.estado == "PROPULSION" and velocidad <= 0 and altitud > 10.0:
            self.estado = "APOGEO"
            evento = "APOGEO_DETECTADO_DROGUE_LIBERADO"
            
        elif self.estado == "APOGEO" and altitud <= 300.0:
            self.estado = "DESCENSO_PRINCIPAL"
            evento = "APERTURA_PARACAIDAS_PRINCIPAL"
            
        elif self.estado == "DESCENSO_PRINCIPAL" and altitud <= 1.0:
            self.estado = "ATERRIZAJE"
            evento = "ATERRIZAJE_CONFIRMADO"
            
        # Registrar en la Caja Negra
        registro = f"{tiempo:.1f},{self.estado},{altitud:.2f},{velocidad:.2f},{evento}\n"
        self.log_file.write(registro)
        self.log_file.flush()
        
        return self.estado, evento

    def cerrar(self):
        if self.log_file:
            self.log_file.close()
        print(f"[BLACK BOX] Vuelo guardado exitosamente en {self.log_filename}")

def ejecutar_mision_completa():
    print("[INICIO] Lanzando simulación de misión completa con Computadora de Vuelo y Black Box...")
    fc = ComputadoraDeVuelo()
    
    dt = 0.1
    # Simular perfil de vuelo de 15 segundos (Subida y bajada)
    alturas_simuladas = [0, 5, 20, 60, 150, 320, 400, 350, 250, 150, 80, 20, 5, 0, 0]
    velocidades_simuladas = [0, 15, 30, 40, 25, 5, -5, -15, -20, -18, -15, -10, -5, 0, 0]
    
    for i in range(len(alturas_simuladas)):
        t = i * dt
        alt = alturas_simuladas[i]
        vel = velocidades_simuladas[i]
        
        estado, evento = fc.update(t, alt, vel) if hasattr(fc, 'update') else fc.actualizar_fsm(t, alt, vel)
        print(f"T: {t:4.1f}s | Estado: {estado:20s} | Alt: {alt:5.1f}m | Vel: {vel:5.1f}m/s | Evento: {evento}")
        time.sleep(0.05)
        
    fc.cerrar()
    print("[FIN] Misión completada y registrada en la caja negra.")

if __name__ == "__main__":
    ejecutar_mision_completa()
