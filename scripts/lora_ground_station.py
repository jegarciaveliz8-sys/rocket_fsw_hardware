import time
from fsw.telemetry_packet import pack_telemetry, unpack_telemetry

def mock_lora_receiver_loop():
    print("Iniciando receptor LoRa en Estación Terrena (915 MHz / 433 MHz)...")
    
    # Simular la recepción de 3 paquetes binarios vía radio
    for seq in range(1, 4):
        sim_alt = seq * 50.0
        sim_vel = 60.0 - (seq * 10.0)
        sim_accel = 5.8 if seq == 1 else 0.5
        
        # Empaquetar como lo haría el microcontrolador en el cohete
        binary_data = pack_telemetry("MIS01", seq, sim_alt, sim_vel, sim_accel)
        
        # Simular recepción en antena
        decoded = unpack_telemetry(binary_data)
        print(f"[LORA RX RF] Recibido paquete #{decoded['seq']} | Alt: {decoded['altitude']}m | Vel: {decoded['velocity']}m/s | Accel: {decoded['acceleration']}G")
        time.sleep(0.5)

if __name__ == "__main__":
    mock_lora_receiver_loop()
