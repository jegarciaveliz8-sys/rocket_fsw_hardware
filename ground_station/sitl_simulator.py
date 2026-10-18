import time
import math

class RocketPhysicsSim:
    def __init__(self):
        self.mass = 1.2 # kg (peso del cohete)
        self.thrust = 80.0 # N (empuje del motor)
        self.burn_time = 2.5 # segundos de quemado del motor
        self.drag_coeff = 0.45
        self.altitude = 0.0
        self.velocity = 0.0
        self.gravity = 9.81
        self.time = 0.0
        self.dt = 0.05 # Tasa de integración (20 Hz)

    def step(self):
        # Fuerza de empuje
        f_thrust = self.thrust if self.time < self.burn_time else 0.0
        
        # Resistencia aerodinámica: Fd = 0.5 * rho * v^2 * Cd * A
        rho = 1.225 # Densidad del aire
        area = 0.0078 # Sección transversal (diámetro 10 cm)
        f_drag = 0.5 * rho * (self.velocity ** 2) * self.drag_coeff * area * math.copysign(1, self.velocity)

        # Fuerza total y aceleración
        f_net = f_thrust - f_drag - (self.mass * self.gravity)
        accel = f_net / self.mass

        # Integración de Euler
        self.velocity += accel * self.dt
        self.altitude += self.velocity * self.dt

        if self.altitude < 0.0:
            self.altitude = 0.0
            self.velocity = 0.0

        self.time += self.dt
        return self.time, accel / self.gravity, self.altitude

sim = RocketPhysicsSim()
print("=== SIMULADOR DE FÍSICA AEROESPACIAL (SITL) ===")
print("Tiempo (s) | Aceleración (G) | Altitud (m)")

for _ in range(120):
    t, g_force, alt = sim.step()
    print(f"{t:6.2f} s  |  {g_force:13.2f} G  |  {alt:8.2f} m")
    time.sleep(0.05)
