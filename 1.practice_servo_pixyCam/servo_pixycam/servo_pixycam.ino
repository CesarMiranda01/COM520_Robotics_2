#include <Pixy2.h>
#include <Servo.h>

Pixy2 pixy;
Servo servoMotor;

int pinServo = 9;       // Pin del servo
int posicionServo = 90; // Posición inicial del servo
int centroCamara = 157; // Centro de la cámara (315/2)
int umbral = 10;        // Margen para considerar el objeto centrado

void setup() {
    Serial.begin(115200);
    pixy.init();          // Inicializar Pixy2
    servoMotor.attach(pinServo);
    servoMotor.write(posicionServo); // Iniciar el servo en 90 grados
}

void loop() {
    pixy.ccc.getBlocks(); // Obtener objetos detectados

    if (pixy.ccc.numBlocks > 0) { // Si hay al menos un objeto detectado
        int x = pixy.ccc.blocks[0].m_x;  // Centro en X
        int y = pixy.ccc.blocks[0].m_y;  // Centro en Y
        int w = pixy.ccc.blocks[0].m_width;  // Ancho del objeto
        int h = pixy.ccc.blocks[0].m_height; // Alto del objeto

        // Calcular esquinas del objeto
        int x1 = x - (w / 2);  // Esquina superior izquierda X
        int y1 = y - (h / 2);  // Esquina superior izquierda Y
        int x2 = x + (w / 2);  // Esquina inferior derecha X
        int y2 = y + (h / 2);  // Esquina inferior derecha Y

        // Calcular la resta de la coordenada inferior derecha menos la inferior izquierda
        int restaX = x2 - x1;
        int restaY = y2 - y1;

        // Mostrar coordenadas
        Serial.print("Centro del objeto - X: ");
        Serial.print(x);
        Serial.print(" | Y: ");
        Serial.println(y);

        Serial.print("Esquina Superior Izquierda - X1: ");
        Serial.print(x1);
        Serial.print(" | Y1: ");
        Serial.println(y1);

        Serial.print("Esquina Inferior Derecha - X2: ");
        Serial.print(x2);
        Serial.print(" | Y2: ");
        Serial.println(y2);

        // Mostrar la resta de las coordenadas
        Serial.print("Resta en X (X2 - X1): ");
        Serial.println(restaX);

        Serial.print("Resta en Y (Y2 - Y1): ");
        Serial.println(restaY);

        // Ajustar servomotor para centrar el objeto
        if (x < (centroCamara - umbral)) {
            posicionServo += 4; // Mover servo a la derecha
        } else if (x > (centroCamara + umbral)) {
            posicionServo -= 4; // Mover servo a la izquierda
        }

        // Limitar el servo entre 0 y 180 grados
        posicionServo = constrain(posicionServo, 0, 180);
        servoMotor.write(posicionServo); // Mover el servo
    } else {
        Serial.println("No se detectó ningún objeto.");
    }

    delay(100);
}
