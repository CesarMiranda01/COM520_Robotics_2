class Rueda {
private:
    int pinPWM;
    int pinIN1;
    int pinIN2;
    int velocidadMinima;
    int velocidadMaxima;
    float correccion;

public:
    Rueda(int pwm, int in2, int in1, int velMin, int velMax, float corr) {
        pinPWM = pwm;
        pinIN1 = in1;
        pinIN2 = in2;
        velocidadMinima = velMin;
        velocidadMaxima = velMax;
        correccion = corr;
        pinMode(pinPWM, OUTPUT);
        pinMode(pinIN1, OUTPUT);
        pinMode(pinIN2, OUTPUT);
    }

    void mover(int velocidad) {
       velocidad = constrain(velocidad, -95, 95);
        int ajusteVelocidad = (int)(map(abs(velocidad), 0, 100, velocidadMinima, velocidadMaxima) * correccion);
        ajusteVelocidad = constrain(ajusteVelocidad, velocidadMinima, velocidadMaxima);

        if (velocidad > 0) {  
            digitalWrite(pinIN1, HIGH);
            digitalWrite(pinIN2, LOW);
            Serial.println("adelante");
        } else if (velocidad < 0) {  
            digitalWrite(pinIN1, LOW);
            digitalWrite(pinIN2, HIGH);
            Serial.println("atras ");
        } else {  
          Serial.println("detenido");
            digitalWrite(pinIN1, LOW);
            digitalWrite(pinIN2, LOW);  // Detener motor
            ajusteVelocidad = 0;  // Asegurar que no gire
        }
  Serial.println(velocidad);
        analogWrite(pinPWM, ajusteVelocidad);
    }
};
