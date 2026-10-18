from fsw.fsm import RocketFSM
import time

def run_fsm_simulation():
    fsm = RocketFSM()
    print(f"Estado inicial: {fsm.state}")
    
    # Simulación paso a paso de un vuelo completo
    trajectory = [
        (2.5, 10.0, 15.0),   # BOOST
        (-1.0, 50.0, 30.0),  # COASTING (ascendiendo rápido)
        (-0.2, 150.0, 5.0),  # COASTING (desacelerando)
        (0.0, 150.2, -0.1),  # APOGEE -> Pasa a DROGUE
        (0.1, 80.0, -12.0),  # DROGUE DESCENT (cruzando 100m) -> Pasa a MAIN
        (0.0, 3.0, -2.0),    # MAIN DESCENT
        (0.0, 0.0, 0.0)      # LANDED
    ]
    
    for i, (accel, alt, vel) in enumerate(trajectory):
        print(f"\n--- Ciclo {i} | Accel: {accel}G | Alt: {alt}m | Vel: {vel}m/s ---")
        fsm.update(accel, alt, vel)
        print(f"Estado actual FSM: {fsm.state}")
        time.sleep(0.2)

if __name__ == "__main__":
    run_fsm_simulation()
