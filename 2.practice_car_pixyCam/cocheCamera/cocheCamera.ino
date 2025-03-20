#include "Tracker.h"
#include "Rueda.h"

// Definir las ruedas del coche
Rueda ruedaIzquierda(5, 8, 9, 40,100, 1.0);  // PWM en 5, IN1 en 4, IN2 en 3, Vel. Mínima 80, Corrección 1.0
Rueda ruedaDerecha(6, 10, 11, 40,100, 1.0);   // PWM en 6, IN1 en 7, IN2 en 8, Vel. Mínima 80, Corrección 0.95

PixyTracker tracker(7, 40, 150, 15); 
void calcularPotencia(int x, float k, int &P_L, int &P_R) {
    // Asegurar que x esté dentro del rango -100 a 100
    x = constrain(x, -100, 100);

    // Calcular potencia de las ruedas
    P_R = constrain(100 - k * x, 0, 200);
    P_L = constrain(100 + k * x, 0, 200);
    int maxPotencia = max(P_L, P_R);

    // Normalizar las potencias para que el valor más grande sea 100
    if (maxPotencia > 0) {
        P_L = map(P_L, 0, maxPotencia, 0, 100);
        P_R = map(P_R, 0, maxPotencia, 0, 100);
    }
}

void setup() {
  Serial.begin(115200);
    tracker.begin();

}

void loop() {

  int xValue = tracker.getSmoothedX();

    if (xValue == 999) {
        ruedaIzquierda.mover(0);  // Detener ruedas
    ruedaDerecha.mover(0);
    } else {
        int P_L, P_R;
    calcularPotencia(xValue, 1.0, P_L, P_R); // Factor k=1.0 para giros normales

    Serial.print("x: "); Serial.print(xValue);
    ruedaIzquierda.mover(P_L);  // Máxima velocidad adelante
    ruedaDerecha.mover(P_R);
    Serial.print(" | P_L: "); Serial.print(P_L);
    Serial.print(" | P_R: "); Serial.println(P_R);
    }

    delay(5);

}
