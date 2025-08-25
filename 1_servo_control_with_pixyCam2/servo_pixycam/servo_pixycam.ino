#include <Pixy2.h>
#include <Servo.h>

Pixy2 pixy;
Servo servoMotor;

int pinServo = 9;       // Servo pin
int servoPosition = 90; // Initial servo position
int cameraCenter = 157; // Camera center (315/2)
int threshold = 10;     // Margin to consider the object centered

void setup() {
    Serial.begin(115200);
    pixy.init();          // Initialize Pixy2
    servoMotor.attach(pinServo);
    servoMotor.write(servoPosition); // Start servo at 90 degrees
}

void loop() {
    pixy.ccc.getBlocks(); // Get detected objects

    if (pixy.ccc.numBlocks > 0) { // If at least one object is detected
        int x = pixy.ccc.blocks[0].m_x;  // Center X
        int y = pixy.ccc.blocks[0].m_y;  // Center Y
        int w = pixy.ccc.blocks[0].m_width;  // Object width
        int h = pixy.ccc.blocks[0].m_height; // Object height

        // Calculate object corners
        int x1 = x - (w / 2);  // Top left corner X
        int y1 = y - (h / 2);  // Top left corner Y
        int x2 = x + (w / 2);  // Bottom right corner X
        int y2 = y + (h / 2);  // Bottom right corner Y

        // Calculate the difference between bottom right and top left coordinates
        int diffX = x2 - x1;
        int diffY = y2 - y1;

        // Display coordinates
        Serial.print("Object Center - X: ");
        Serial.print(x);
        Serial.print(" | Y: ");
        Serial.println(y);

        Serial.print("Top Left Corner - X1: ");
        Serial.print(x1);
        Serial.print(" | Y1: ");
        Serial.println(y1);

        Serial.print("Bottom Right Corner - X2: ");
        Serial.print(x2);
        Serial.print(" | Y2: ");
        Serial.println(y2);

        // Display coordinate differences
        Serial.print("Difference in X (X2 - X1): ");
        Serial.println(diffX);

        Serial.print("Difference in Y (Y2 - Y1): ");
        Serial.println(diffY);

        // Adjust servomotor to center the object
        if (x < (cameraCenter - threshold)) {
            servoPosition += 4; // Move servo to the right
        } else if (x > (cameraCenter + threshold)) {
            servoPosition -= 4; // Move servo to the left
        }

        // Limit servo between 0 and 180 degrees
        servoPosition = constrain(servoPosition, 0, 180);
        servoMotor.write(servoPosition); // Move the servo
    } else {
        Serial.println("No object detected.");
    }

    delay(100);
}