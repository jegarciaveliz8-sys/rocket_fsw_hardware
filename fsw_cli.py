import os
import sys

def mostrar_menu():
    print("\n==================================================")
    print("      SISTEMA DE SOFTWARE DE VUELO (FSW)          ")
    print("==================================================")
    print("1. Compilar y ejecutar pruebas de código C++ (GTest)")
    print("2. Ejecutar Simulación Hardware-in-the-Loop (HIL)")
    print("3. Procesar telemetría y generar gráficos (Python)")
    print("4. Lanzar Interfaz Gráfica de Estación Terrena (Tkinter GUI)")
    print("5. Ejecutar análisis del Filtro de Kalman (EKF)")
    print("6. Correr batería de pruebas automáticas (Pytest)")
    print("7. Ejecutar simulación 6-DOF con RocketPy")
    print("8. Visualizador 3D Avanzado (Humo + Mapa Táctico GPS)")
    print("9. Exportar reportes de misión a Google Drive / PDF")
    print("10. Iniciar Servidor Web de Estación Terrena (FastAPI / WebSockets)")
    print("11. Ejecutar Simulación Realista con Ruido de Sensores y Viento")
    print("12. Ejecutar Simulación EKF con Datos Realistas (Filtro Activo)")
    print("13. Ejecutar Computadora de Vuelo Completa (FSM + Black Box)")
    print("0. Salir")
    print("==================================================")

def ejecutar_opcion(opcion):
    if opcion == '1':
        os.system("mkdir -p build && cd build && cmake .. && make && ctest --output-on-failure")
    elif opcion == '2':
        os.system("python3 sim/hil_simulation.py")
    elif opcion == '3':
        os.system("python3 sim/telemetry_analysis.py")
    elif opcion == '4':
        os.system("python3 gui/ground_station_gui.py")
    elif opcion == '5':
        os.system("python3 sim/ekf_analysis.py")
    elif opcion == '6':
        os.system("pytest")
    elif opcion == '7':
        os.system("python3 sim/rocket_model.py")
    elif opcion == '8':
        os.system("python3 sim/visualizador_3d.py")
    elif opcion == '9':
        os.system("python3 tools/export_reports.py")
    elif opcion == '10':
        os.system("uvicorn web.server:app --reload")
    elif opcion == '11':
        os.system("python3 sim/simulacion_realista.py")
    elif opcion == '12':
        os.system("python3 sim/ekf_realista.py")
    elif opcion == '13':
        os.system("python3 sim/flight_computer.py")
    elif opcion == '0':
        print("[INFO] Saliendo del CLI de Aviónica. ¡Buen vuelo!")
        sys.exit(0)
    else:
        print("[ERROR] Opción no válida. Intente de nuevo.")

def main():
    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción: ").strip()
        ejecutar_opcion(opcion)

if __name__ == "__main__":
    main()
