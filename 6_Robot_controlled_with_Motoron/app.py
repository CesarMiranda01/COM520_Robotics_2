import time
import motoron

# --- Configuration ---
MOTORON_ADDR_LEFT = 16    # I2C address for the Motoron controlling left wheels
MOTORON_ADDR_RIGHT = 17   # I2C address for the Motoron controlling right wheels

# Motor IDs on each Motoron board (M1=0, M2=1, M3=2 as per library/hardware)
# We are using M2 and M3 as per your request.
# Note: The library's set_speed/set_max_acceleration methods often use 1-based indexing
# for motor numbers (e.g., motor 1, 2, 3).
# However, internally, Pololu documentation sometimes refers to them as M1, M2, M3.
# The motoron.py library functions like mc.set_max_acceleration(motor_number, value)
# expect motor_number to be 1, 2, or 3.
MOTOR_M2 = 2 # Corresponds to M2 (usually motor_number=2 in library functions)
MOTOR_M3 = 3 # Corresponds to M3 (usually motor_number=3 in library functions)

DEFAULT_SPEED = 400  # Motor speed (-800 to 800). Adjust as needed.
MOVE_DURATION = 3    # Duration for forward/backward movements in seconds
TURN_DURATION = 1.5  # Duration for turns in seconds
PAUSE_DURATION = 1   # Pause between movements

# --- Initialize Motoron Controllers ---
try:
    print(f"Initializing Motoron (Left Wheels) at I2C address {MOTORON_ADDR_LEFT}...")
    mc_left = motoron.MotoronI2C(address=MOTORON_ADDR_LEFT)
    mc_left.reinitialize()  # Reset to default settings
    # mc_left.disable_crc()   # Optional: disable CRC if not needed or causes issues
    mc_left.clear_reset_flag()

    print(f"Initializing Motoron (Right Wheels) at I2C address {MOTORON_ADDR_RIGHT}...")
    mc_right = motoron.MotoronI2C(address=MOTORON_ADDR_RIGHT)
    mc_right.reinitialize() # Reset to default settings
    # mc_right.disable_crc()  # Optional
    mc_right.clear_reset_flag()

    # Optional: Disable command timeout if you prefer manual stop/start
    # mc_left.disable_command_timeout()
    # mc_right.disable_command_timeout()

    # --- Configure Motors on Left Controller (mc_left) ---
    # Configure M2 on left controller
    mc_left.set_max_acceleration(MOTOR_M2, 160)
    mc_left.set_max_deceleration(MOTOR_M2, 160)
    # Configure M3 on left controller
    mc_left.set_max_acceleration(MOTOR_M3, 160)
    mc_left.set_max_deceleration(MOTOR_M3, 160)

    # --- Configure Motors on Right Controller (mc_right) ---
    # Configure M2 on right controller
    mc_right.set_max_acceleration(MOTOR_M2, 160)
    mc_right.set_max_deceleration(MOTOR_M2, 160)
    # Configure M3 on right controller
    mc_right.set_max_acceleration(MOTOR_M3, 160)
    mc_right.set_max_deceleration(MOTOR_M3, 160)

    print("Motorons initialized and configured.")

except Exception as e:
    print(f"Error during Motoron initialization: {e}")
    print("Please check I2C connections, addresses, and Motoron power.")
    exit()

# --- Movement Functions ---
def stop_all_motors():
    # Stop M2 and M3 on left controller
    mc_left.set_speed(MOTOR_M2, 0)
    mc_left.set_speed(MOTOR_M3, 0)
    # Stop M2 and M3 on right controller
    mc_right.set_speed(MOTOR_M2, 0)
    mc_right.set_speed(MOTOR_M3, 0)
    print("All motors stopped.")

def move_forward(speed):
    print("Moving forward...")
    # Left wheels forward
    mc_left.set_speed(MOTOR_M2, speed)
    mc_left.set_speed(MOTOR_M3, speed)
    # Right wheels forward
    mc_right.set_speed(MOTOR_M2, speed)
    mc_right.set_speed(MOTOR_M3, speed)

def move_backward(speed):
    print("Moving backward...")
    # Left wheels backward
    mc_left.set_speed(MOTOR_M2, -speed)
    mc_left.set_speed(MOTOR_M3, -speed)
    # Right wheels backward
    mc_right.set_speed(MOTOR_M2, -speed)
    mc_right.set_speed(MOTOR_M3, -speed)

def turn_right(speed):
    print("Turning right...")
    # Left wheels forward
    mc_left.set_speed(MOTOR_M2, speed)
    mc_left.set_speed(MOTOR_M3, -speed)
    # Right wheels backward
    mc_right.set_speed(MOTOR_M2, -speed)
    mc_right.set_speed(MOTOR_M3, speed)

def turn_left(speed):
    print("Turning left...")
    # Left wheels backward
    mc_left.set_speed(MOTOR_M2, -speed)
    mc_left.set_speed(MOTOR_M3, speed)
    # Right wheels forward
    mc_right.set_speed(MOTOR_M2, speed)
    mc_right.set_speed(MOTOR_M3, -speed)

# --- Main Movement Sequence ---
try:
    print("\nStarting movement sequence...")

    # Move Forward
    move_forward(DEFAULT_SPEED)
    time.sleep(MOVE_DURATION)
    stop_all_motors()
    time.sleep(PAUSE_DURATION)

    # Move Backward
    move_backward(DEFAULT_SPEED)
    time.sleep(MOVE_DURATION)
    stop_all_motors()
    time.sleep(PAUSE_DURATION)

    # Turn Right
    turn_right(DEFAULT_SPEED)
    time.sleep(TURN_DURATION)
    stop_all_motors()
    time.sleep(PAUSE_DURATION)

    # Turn Left
    turn_left(DEFAULT_SPEED)
    time.sleep(TURN_DURATION)
    stop_all_motors()
    # No pause needed after the last movement

    print("\nMovement sequence completed.")

except KeyboardInterrupt:
    print("\nProgram interrupted by user (Ctrl+C).")
except Exception as e:
    print(f"\nAn error occurred during the movement sequence: {e}")
finally:
    # Ensure all motors are stopped when the script ends or if an error occurs
    print("Ensuring all motors are stopped before exiting.")
    stop_all_motors()