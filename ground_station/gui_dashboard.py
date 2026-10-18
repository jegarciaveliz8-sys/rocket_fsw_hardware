import tkinter as tk
from tkinter import ttk
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class AdvancedGroundStationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AeroSpace Mission Control - Live Telemetry & EKF")
        self.root.geometry("800x600")
        self.root.configure(bg="#1e1e1e")

        title_label = tk.Label(root, text="MISION CONTROL FSW v2.0 - LIVE", fg="#00ffcc", bg="#1e1e1e", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        # Configuración del gráfico de Matplotlib
        self.fig, self.ax = plt.subplots(figsize=(7, 4), dpi=100)
        self.fig.patch.set_facecolor('#2d2d2d')
        self.ax.set_facecolor('#1e1e1e')
        
        self.times = []
        self.altitudes = []
        self.line, = self.ax.plot(self.times, self.altitudes, color='#00ffcc', linewidth=2, label="Altitud EKF (m)")
        
        self.ax.set_title("Trayectoria de Vuelo en Tiempo Real", color='white', fontsize=10)
        self.ax.set_xlabel("Tiempo (s)", color='white')
        self.ax.set_ylabel("Altitud (m)", color='white')
        self.ax.tick_params(colors='white')
        self.ax.grid(True, linestyle='--', alpha=0.3)
        self.ax.legend(loc="upper left")

        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(pady=10)

        # Botón de simulación en vivo
        self.btn_run = ttk.Button(root, text="Iniciar Simulación Gráfica", command=self.run_live_simulation)
        self.btn_run.pack(pady=10)

        self.sim_step = 0

    def run_live_simulation(self):
        if self.sim_step < 50:
            t = self.sim_step * 0.2
            alt = max(0, 150 * math.sin(t / 3.0) + random.gauss(0, 2)) if t < 10 else 0
            
            self.times.append(t)
            self.altitudes.append(alt)
            
            self.line.set_xdata(self.times)
            self.line.set_ydata(self.altitudes)
            self.ax.relim()
            self.ax.autoscale_view()
            self.canvas.draw()
            
            self.sim_step += 1
            self.root.after(100, self.run_live_simulation)

if __name__ == "__main__":
    import math
    root = tk.Tk()
    app = AdvancedGroundStationGUI(root)
    root.mainloop()
