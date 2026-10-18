#pragma once

enum FlightState {
    IDLE = 0,
    BOOST = 1,
    COAST = 2,
    APOGEE = 3,
    RECOVERY = 4
};

void updateFlightState(float az, float current_altitude);
FlightState getCurrentFlightState();
