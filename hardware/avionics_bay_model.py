import math

class AvionicsBayChassis:
    def __init__(self, inner_diameter_mm=95.0, length_mm=150.0):
        self.id_mm = inner_diameter_mm
        self.length = length_mm
        self.material = "PETG / Fibra de Carbono"

    def calculate_structural_volume(self):
        # Cálculo del volumen del cilindro contenedor
        radius = self.id_mm / 2.0
        cross_section_area = math.pi * (radius ** 2)
        internal_volume_cm3 = (cross_section_area * self.length) / 1000.0
        return internal_volume_cm3

    def print_specs(self):
        print("=== ESPECIFICACIONES DE CHASIS 3D (AVIONICS BAY) ===")
        print(f"Diámetro Interno: {self.id_mm} mm")
        print(f"Longitud del Módulo: {self.length} mm")
        print(f"Volumen Interno Disponible: {self.calculate_structural_volume():.2f} cm³")
        print(f"Material Recomendado de Impresión: {self.material}")

if __name__ == "__main__":
    bay = AvionicsBayChassis()
    bay.print_specs()
