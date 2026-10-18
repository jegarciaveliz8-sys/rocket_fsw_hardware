#ifndef MATH_QUAT_H
#define MATH_QUAT_H

#include <cmath>

struct Quaternion {
    float w = 1.0f;
    float x = 0.0f;
    float y = 0.0f;
    float z = 0.0f;

    void normalize() {
        float norm = std::sqrt(w*w + x*x + y*y + z*z);
        if (norm > 0.0f) {
            w /= norm; x /= norm; y /= norm; z /= norm;
        }
    }

    void integrate(float p, float q, float r, float dt) {
        float dq_w = 0.5f * (-x*p - y*q - z*r);
        float dq_x = 0.5f * ( w*p + y*r - z*q);
        float dq_y = 0.5f * ( w*q - x*r + z*p);
        float dq_z = 0.5f * ( w*r + x*q - y*p);

        w += dq_w * dt;
        x += dq_x * dt;
        y += dq_y * dt;
        z += dq_z * dt;
        normalize();
    }
};

#endif
