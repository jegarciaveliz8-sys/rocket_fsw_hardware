import tkinter as tk
from tkinter import ttk
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class GroundStationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Rocket FSW - Estación Terrena en Vivo")
        self.root.geometry("800x600")
        
        title_label = ttk.Label(root, text="ESTACIÓN TERRENA - TELEMETRÍA GNC", font=("Arial", 14, "bold"))
        title_label.pack(pady=10)
        
        # Panel de datos actuales
        self.frame_metrics = ttk.LabelFrame(root, text="Métricas de Vuelo Actuales")
        self.frame_metrics.pack(fill="x", padx=20, pady=10)
        
        self.lbl_alt = ttk.Label(self.frame_metrics, text="Altitud: 0.0 m", font=("Arial", 12))
        self.lbl_alt.pack(side="left", padx=20, pady=10)
        
        self.lbl_vel = ttk.Label(self.frame_metrics, text="Velocidad: 0.0 m/s", font=("Arial", 12))
        self.lbl_vel.pack(side="left", padx=20, pady=10)
        
        self.lbl_accel = ttk.Label(self.frame_metrics, text="Aceleración: 0.0 G", font=("Arial", 12))
        self.lbl_accel.pack(side="left", padx=20, pady=10)
        
        # Gráfica Matplotlib
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.x_data = []
        self.y_alt_data = []
        
        self.ax.set_title("Perfil de Altitud en Tiempo Real")
        self.ax.set_xlabel("Tiempo (s)")
        self.ax.set_ylabel("Altitud (m)")
        
        self.line, = self.ax.plot([], [], 'r-', marker='o')
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=10)
        
        self.time_counter = 0
        self.update_simulation()

    def update_simulation(self):
        self.time_counter += 1
        # Simular datos dinámicos de vuelo
        sim_alt = max(0.0, 150.0 * (1 - ((self.time_counter - 5)**2 / 25.0))) if self.time_counter <= 10 else 0.0
        sim_vel = 60.0 - (self.time_counter * 6.0)
        sim_accel = 5.8 if self.time_counter == 1 else 0.2
        
        # Actualizar etiquetas
        self.lbl_alt.config(text=f"Altitud: {sim_alt:.1f} m")
        self.lbl_vel.config(text=f"Velocidad: {sim_vel:.1f} m/s")
        self.lbl_accel.config(text=f"Aceleración: {sim_accel:.1f} G")
        
        # Actualizar gráfica
        self.x_data.append(self.time_counter)
        self.y_alt_data.append(sim_alt)
        
        self.line.set_xdata(self.x_data)
        self.line.set_ydata(self.y_alt_data)
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()
        
        if self.time_counter < 15:
            self.root.after(1000, self.update_simulation)

def launch_gui():
    root = tk.Tk()
    app = GroundStationGUI(root)
    root.mainloop()

if __name__ == "__main__":
    launch_gui()
