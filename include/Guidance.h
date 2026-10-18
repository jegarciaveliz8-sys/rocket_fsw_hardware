#ifndef GUIDANCE_H
#define GUIDANCE_H

class ProportionalNavigation {
private:
    float nav_constant; // Ganancia de navegación (N = 3.0 a 5.0)

public:
    ProportionalNavigation(float N = 4.0f) : nav_constant(N) {}

    float computeCommand(float closing_velocity, float los_rate) {
        return nav_constant * closing_velocity * los_rate;
    }
};

#endif
