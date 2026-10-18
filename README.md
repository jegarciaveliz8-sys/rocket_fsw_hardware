# Rocket Flight Software (FSW) & GNC Ecosystem

Sistema embebido de vuelo y estación terrena en bucle cerrado para cohetería experimental, diseñado con arquitectura de control GNC (EKF + PID), simulación Hardware-in-the-Loop (SITL), telemetría binaria y procesamiento de caja negra.

## Arquitectura del Proyecto
* src/ & include/: Código base de firmware, estimador de estado EKF, controlador PID de aletas y drivers simulados de sensores.
* ground_station/: Servidor UDP de telemetría, almacenamiento de caja negra (flight_blackbox.bin) e interfaz gráfica de misión (gui_dashboard.py).
* scripts/: Orquestador de misión completa y analizador de datos post-vuelo.
* tests/: Pruebas unitarias avanzadas para validación matemática de GNC.

## Panel de Control Maestro (CLI)
Para interactuar con todo el ecosistema de forma centralizada:
python fsw_cli.py

## Ejecución de Componentes
* Simulación de Misión y Análisis Post-Vuelo:
  python scripts/run_full_mission.py
  python scripts/flight_analyzer.py
* Estación Terrena (GUI):
  python ground_station/gui_dashboard.py
