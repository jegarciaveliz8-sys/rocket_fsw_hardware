import pandas as pd
import matplotlib.pyplot as plt

def analyze_flight():
    print("[Análisis Post-Vuelo] Leyendo caja negra 'blackbox_log.csv'...")
    try:
        # Cargar datos de la caja negra
        df = pd.read_csv('blackbox_log.csv')
        
        # Calcular métricas de rendimiento
        max_accel = df['AccelZ'].max()
        min_accel = df['AccelZ'].min()
        avg_accel = df['AccelZ'].mean()
        total_samples = len(df)
        flight_duration = df['Tiempo'].iloc[-1]

        print("\n--- REPORTE DE MISIÓN (CAJA NEGRA) ---")
        print(f"Duración del Vuelo: {flight_duration:.2f} s")
        print(f"Muestras registradas: {total_samples}")
        print(f"Aceleración Z Máxima: {max_accel:.2f} m/s^2")
        print(f"Aceleración Z Mínima: {min_accel:.2f} m/s^2")
        print(f"Aceleración Z Promedio: {avg_accel:.2f} m/s^2")
        print("---------------------------------------\n")

        # Generar gráfico estático detallado del post-vuelo
        plt.figure(figsize=(10, 5))
        plt.plot(df['Tiempo'], df['AccelZ'], label='Aceleración Z (IMU)', color='purple')
        plt.plot(df['Tiempo'], df['PitchCmd'], label='Comando Actuador Pitch', color='orange', linestyle='--')
        plt.title("Análisis Post-Vuelo - Historial de Caja Negra")
        plt.xlabel("Tiempo (s)")
        plt.ylabel("Valores de Sistema")
        plt.grid(True)
        plt.legend()
        plt.savefig("flight_report.png")
        print("Gráfico de reporte guardado como 'flight_report.png'.")
        plt.show()

    except FileNotFoundError:
        print("[Error] No se encontró el archivo 'blackbox_log.csv'. Asegúrate de haber ejecutado el FSW antes.")

if __name__ == "__main__":
    analyze_flight()
