import random
import math

class MonteCarloTrajectorySim:
    def __init__(self, num_simulations=200):
        self.num_simulations = num_simulations
        self.landing_points = []

    def run_simulations(self):
        print(f"=== INICIANDO SIMULACIÓN MONTE CARLO ({self.num_simulations} VUELOS) ===")
        
        for i in range(self.num_simulations):
            # Parámetros nominales con variaciones estocásticas (Gaussiana / Uniforme)
            wind_speed_m_s = random.gauss(3.0, 1.5)      # Viento medio con desviación
            motor_thrust_n = random.gauss(80.0, 4.0)     # Variación de empuje del motor
            rocket_mass_kg = random.gauss(1.2, 0.05)     # Tolerancia de peso estructural
            
            # Modelo simplificado de deriva por viento y apogeo
            burn_time = 2.5
            effective_thrust = motor_thrust_n / rocket_mass_kg
            max_altitude = (effective_thrust * (burn_time ** 2)) * 3.2 + random.gauss(0, 15.0)
            
            # Deriva lateral calculada por la velocidad del viento durante el descenso en paracaídas
            desfall_time = math.sqrt(2.0 * max_altitude / 9.81) * 1.8 # Tiempo de caída
            lateral_drift_m = wind_speed_m_s * desfall_time + random.gauss(0, 5.0)
            
            # Dirección de deriva aleatoria (0 a 360 grados)
            angle_rad = random.uniform(0, 2 * math.pi)
            pos_x = lateral_drift_m * math.cos(angle_rad)
            pos_y = lateral_drift_m * math.sin(angle_rad)
            
            self.landing_points.append((pos_x, pos_y, max_altitude))

    def analyze_results(self):
        altitudes = [p[2] for p in self.landing_points]
        drifts = [math.sqrt(p[0]**2 + p[1]**2) for p in self.landing_points]
        
        min_alt = min(altitudes)
        max_alt = max(altitudes)
        avg_alt = sum(altitudes) / len(altitudes)
        
        max_radius = max(drifts)
        
        print(f"\n--- RESULTADOS ESTADÍSTICOS MONTE CARLO ---")
        print(f"Altitud Mínima Predicha: {min_alt:.2f} m")
        print(f"Altitud Máxima Predicha: {max_alt:.2f} m")
        print(f"Altitud Promedio: {avg_alt:.2f} m")
        print(f"Radio Máximo de Dispersión (Elipse de Impacto): {max_radius:.2f} m")
        print(f">>> ANÁLISIS DE DISPERSIÓN COMPLETADO CON ÉXITO EXTREMO <<<")

if __name__ == "__main__":
    sim = MonteCarloTrajectorySim(200)
    sim.run_simulations()
    sim.analyze_results()
