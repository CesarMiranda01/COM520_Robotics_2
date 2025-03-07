// PRACTICE 

#include <Pixy2.h>
#include <Servo.h>

Pixy2 pixy;       // Objeto para comunicarse con Pixy2
Servo servoMotor; // Objeto para el servomotor

int pinServo = 9;       // Pin donde está conectado el servomotor
int posicionServo = 90; // Posición inicial del servo (centrado)
int centroCamara = 157; // Valor X del centro de la cámara (315/2)
int umbral = 10;        // Rango aceptable para considerar que el objeto está centrado

void setup() {
    Serial.begin(115200);
    pixy.init();          // Inicializar la cámara Pixy2
    servoMotor.attach(pinServo);
    servoMotor.write(posicionServo); // Iniciar el servo en 90 grados
}

void loop() {
    pixy.ccc.getBlocks(); // Obtener los bloques detectados

    if (pixy.ccc.numBlocks > 0) { // Si se detecta un objeto
        int x = pixy.ccc.blocks[0].m_x; // Obtener coordenada X

        Serial.print("Objeto detectado en X: ");
        Serial.println(x);

        // Ajustar el servomotor para centrar el objeto
        if (x < (centroCamara - umbral)) {
            posicionServo += 4; // Girar hacia la derecha
        } else if (x > (centroCamara + umbral)) {
            posicionServo -= 4; // Girar hacia la izquierda
        }

        // Limitar la posición del servo entre 0 y 180 grados
        posicionServo = constrain(posicionServo, 0, 180);
        servoMotor.write(posicionServo); // Mover el servo
    } else {
        Serial.println("Objeto amarillo NO detectado.");
    }

    delay(100); // Pequeña pausa antes de la siguiente lectura
}
