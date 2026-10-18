#pragma once
#include <Arduino.h>

// Pines de actuadores / pirotecnia
const int PYRO_PIN = 23; 

// Pin CS para la ranura SD integrada de la Teensy 4.1
#ifndef BUILTIN_SDCARD
#define BUILTIN_SDCARD 254
#endif
const int SD_CS_PIN = BUILTIN_SDCARD;

// Umbrales de vuelo aeroespacial
const float LAUNCH_ACCEL_THRESHOLD = 3.0; // Gs
const float APOGEE_ALTITUDE_DROP = 1.0;   // Metros de descenso respecto al apogeo para confirmar eyección
