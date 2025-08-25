#include "Tracker.h"
#include "Rueda.h"

// Define car wheels
Rueda ruedaIzquierda(5, 8, 9, 40, 100, 1.0);  // PWM pin 5, IN1 pin 4, IN2 pin 3, Min Speed 80, Correction 1.0
Rueda ruedaDerecha(6, 10, 11, 40, 100, 1.0);   // PWM pin 6, IN1 pin 7, IN2 pin 8, Min Speed 80, Correction 0.95

PixyTracker tracker(7, 40, 150, 15);

void calculatePower(int x, float k, int &P_L, int &P_R) {
    // Ensure x is within -100 to 100 range
    x = constrain(x, -100, 100);

    // Calculate wheel power
    P_R = constrain(100 - k * x, 0, 200);
    P_L = constrain(100 + k * x, 0, 200);
    int maxPower = max(P_L, P_R);

    // Normalize power values so the largest is 100
    if (maxPower > 0) {
        P_L = map(P_L, 0, maxPower, 0, 100);
        P_R = map(P_R, 0, maxPower, 0, 100);
    }
}

void setup() {
    Serial.begin(115200);
    tracker.begin();
}

void loop() {
    int xValue = tracker.getSmoothedX();

    if (xValue == 999) {
        ruedaIzquierda.mover(0);  // Stop wheels
        ruedaDerecha.mover(0);
    } else {
        int P_L, P_R;
        calculatePower(xValue, 1.0, P_L, P_R); // k factor=1.0 for normal turns

        Serial.print("x: "); Serial.print(xValue);
        ruedaIzquierda.mover(P_L);  // Maximum forward speed
        ruedaDerecha.mover(P_R);
        Serial.print(" | P_L: "); Serial.print(P_L);
        Serial.print(" | P_R: "); Serial.println(P_R);
    }

    delay(5);
}