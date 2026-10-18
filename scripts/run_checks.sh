#!/bin/bash
set -e

echo "=== [1/4] Compilando y ejecutando pruebas de Algoritmos GNC ==="
g++ -std=c++11 -Iinclude src/guidance_test.cpp -o guidance_test
./guidance_test
rm -f guidance_test

echo "=== [2/4] Ejecutando Simulador Físico (SITL) ==="
python ground_station/sitl_simulator.py > /dev/null
echo "SITL OK."

echo "=== [3/4] Validando Parser de Telemetría Binaria ==="
python ground_station/binary_parser.py > /dev/null
echo "Binary Parser OK."

echo "=== [4/4] Ejecutando Simulación Monte Carlo ==="
python ground_station/monte_carlo_sim.py > /dev/null
echo "Monte Carlo OK."

echo ">>> TODOS LOS CONTROLES DE CALIDAD AEROESPACIAL PASARON CON ÉXITO EXTREMO <<<"
