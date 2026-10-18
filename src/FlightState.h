#ifndef FLIGHT_STATE_H
#define FLIGHT_STATE_H

enum FlightState {
    PRE_LAUNCH,
    ARMED,
    LIFTOFF,
    POWERED_FLIGHT,
    COASTING,
    RECOVERY
};

#endif
