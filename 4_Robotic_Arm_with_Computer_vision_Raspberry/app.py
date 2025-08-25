import cv2
import numpy as np
from Servo import Servo

# Servo initialization
shoulder = Servo(22)
elbow = Servo(17)
wrist = Servo(18)
gripper = Servo(27)

def initialize():
    shoulder.move_to_angle(90)
    elbow.move_to_angle(35)
    wrist.move_to_angle(90)
    gripper.move_to_angle(0)

def openGripper():
    gripper.smooth_move(53, 0)

def closeGripper():
    gripper.smooth_move(0, 53)

def pickLeft():
    shoulder.smooth_move(90, 115)
    elbow.smooth_move(35, 130)
    wrist.smooth_move(90, 20)
    closeGripper()
    wrist.smooth_move(20, 90)
    shoulder.smooth_move(115, 90)
    elbow.smooth_move(130, 35)
    openGripper()

def pickCenter():
    shoulder.smooth_move(90, 80)
    elbow.smooth_move(35, 130)
    wrist.smooth_move(90, 20)
    closeGripper()
    wrist.smooth_move(20, 90)
    shoulder.smooth_move(80, 90)
    elbow.smooth_move(130, 35)
    openGripper()

def pickRight():
    shoulder.smooth_move(90, 40)
    elbow.smooth_move(35, 130)
    wrist.smooth_move(90, 20)
    closeGripper()
    wrist.smooth_move(20, 90)
    shoulder.smooth_move(40, 90)
    elbow.smooth_move(130, 35)
    openGripper()

LOWER_COLOR = np.array([35, 100, 100])  # Adjust as needed
UPPER_COLOR = np.array([85, 255, 255])

# Function to control robot arm based on object position
def control_robot_arm(position):
    if position == 'Left':
        pickLeft()
        initialize()
    if position == 'Right':
        pickRight()
        initialize()
    if position == 'Center':
        pickCenter()
        initialize()

initialize()
# Initialize camera
cap = cv2.VideoCapture(0)

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_width = frame.shape[1]  # Get frame width
        left_threshold = frame_width // 3
        right_threshold = 2 * frame_width // 3

        # Convert to HSV and apply color mask
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, LOWER_COLOR, UPPER_COLOR)
        
        # Find contours of detected object
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        object_position = None  # Initialize object position variable
        
        if contours:
            # Select the largest contour
            largest_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour)
            object_x = x + w // 2  # X coordinate of object center
            
            # Determine object position
            if object_x < left_threshold:
                object_position = "Left"
            elif object_x > right_threshold:
                object_position = "Right"
            else:
                object_position = "Center"
            
            # Draw rectangle around detected object (green) and blue frame
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.rectangle(frame, (x - 10, y - 10), (x + w + 10, y + h + 10), (255, 0, 0), 2)  # Blue frame
            cv2.putText(frame, f"{object_position}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            print(f"Search Mode - Position: {object_position}")
        
        # Check if 'a' key was pressed and object is detected
        key = cv2.waitKey(1) & 0xFF
        if key == ord('a') and object_position is not None:
            print("'a' key pressed, switching to action mode...")
            control_robot_arm(object_position)
        
        # Display image
        cv2.imshow("Frame", frame)
        
        # Exit with 'q' key
        if key == ord('q'):
            print("Exiting program...")
            break
finally:
    cap.release()
    shoulder.cleanup()
    cv2.destroyAllWindows()