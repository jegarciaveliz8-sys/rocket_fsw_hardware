# Guía de Fabricación y Ensamblaje PCB - Rocket FSW v2.0

## 1. Especificaciones de Producción (Gerber & Drill)
- **Capas (Layers):** 2 Capas (Top Copper, Bottom Copper).
- **Grosor de la placa:** 1.6 mm.
- **Material base:** FR-4 (TG 130-140°C para soportar vibraciones térmicas de lanzamiento).
- **Acabado superficial:** ENIG (Gold Flash) recomendado para resistencia a la corrosión y mejor contacto en conectores.
- **Ancho de pistas de potencia (Pirotecnia):** Mínimo 2.0 mm (75 mils) para soportar corrientes transitorias de ignición de 3A.

## 2. Archivos Requeridos para Envío a Planta (Gerber Package)
1. `rocket_fsw-F_Cu.gtl` (Capa de Cobre Superior)
2. `rocket_fsw-B_Cu.gbl` (Capa de Cobre Inferior)
3. `rocket_fsw-F_Mask.gts` (Máscara de Solder Mask Superior)
4. `rocket_fsw-B_Mask.gbs` (Máscara de Solder Mask Inferior)
5. `rocket_fsw-F_Silk.gto` (Serigrafía Superior)
6. `rocket_fsw-Edge_Cuts.gm1` (Contorno y dimensiones de la tarjeta)
7. `rocket_fsw.drl` (Archivo de taladrado y perforaciones NC Drill)
