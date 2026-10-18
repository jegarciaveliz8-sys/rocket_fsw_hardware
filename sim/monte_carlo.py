import random
import statistics

def run_monte_carlo(runs=20):
    print(f"\n--- INICIANDO SIMULACIÓN MONTE CARLO ({runs} ITERACIONES) ---")
    apogees = []
    landings = []
    
    for i in range(runs):
        # Variaciones estocásticas (perturbaciones atmosféricas y de motor)
        wind_variation = random.gauss(0.0, 2.5)       # m/s
        mass_variation = random.gauss(1.0, 0.05)      # factor de masa
        angle_variation = random.gauss(0.0, 1.5)      # grados de desviación en rampa
        
        # Simulación simplificada basada en física estocástica
        sim_apogee = 150.0 + (wind_variation * 1.2) - (mass_variation * 5.0) - abs(angle_variation * 2.0)
        sim_landing = 50.0 + (wind_variation * 8.5) + (angle_variation * 12.0)
        
        apogees.append(sim_apogee)
        landings.append(sim_landing)
        
    mean_apogee = statistics.mean(apogees)
    std_apogee = statistics.stdev(apogees)
    mean_landing = statistics.mean(landings)
    std_landing = statistics.stdev(landings)
    
    print(f"Resultados Estadísticos Monte Carlo:")
    print(f" - Apogeo Promedio: {mean_apogee:.2f} m (Desv. Est: {std_apogee:.2f} m)")
    print(f" - Zona de Caída Promedio: {mean_landing:.2f} m del pad (Desv. Est: {std_landing:.2f} m)")
    print("--- ANÁLISIS MONTE CARLO FINALIZADO ---\n")

if __name__ == "__main__":
    run_monte_carlo()
