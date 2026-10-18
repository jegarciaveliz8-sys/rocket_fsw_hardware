#ifndef CONTROL_H
#define CONTROL_H

#include <algorithm>

class ActuatorMixer {
public:
    void mix(float pitch_cmd, float yaw_cmd, float roll_cmd, int &pwm1, int &pwm2, int &pwm3, int &pwm4) {
        float fin1 = 1500.0f + pitch_cmd + roll_cmd;
        float fin2 = 1500.0f + yaw_cmd   - roll_cmd;
        float fin3 = 1500.0f - pitch_cmd + roll_cmd;
        float fin4 = 1500.0f - yaw_cmd   - roll_cmd;

        pwm1 = static_cast<int>(std::clamp(fin1, 1000.0f, 2000.0f));
        pwm2 = static_cast<int>(std::clamp(fin2, 1000.0f, 2000.0f));
        pwm3 = static_cast<int>(std::clamp(fin3, 1000.0f, 2000.0f));
        pwm4 = static_cast<int>(std::clamp(fin4, 1000.0f, 2000.0f));
    }
};

#endif
