import RPi.GPIO as GPIO
import time

class Servo:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        self.pwm = GPIO.PWM(self.pin, 50)  # 50 Hz frequency
        self.pwm.start(0)
    
    def set_angle(self, angle, delay=0.02):
        duty_cycle = (angle / 18) + 2  # Angle to duty cycle conversion
        self.pwm.ChangeDutyCycle(duty_cycle)
        time.sleep(delay)
    
    def move_to_angle(self, angle):
        """Move servo directly to an angle without smooth movement."""
        duty_cycle = (angle / 18) + 2
        self.pwm.ChangeDutyCycle(duty_cycle)
        time.sleep(0.5)  # Wait to ensure movement
        self.pwm.ChangeDutyCycle(0)  # Stop PWM to avoid vibrations
    
    def smooth_move(self, start_angle, end_angle, step=1, delay=0.02):
        step = step if start_angle < end_angle else -step
        for angle in range(start_angle, end_angle + step, step):
            self.set_angle(angle, delay)
        self.pwm.ChangeDutyCycle(0)  # Stop PWM pulse after movement
    
    def cleanup(self):
        self.pwm.stop()
        GPIO.cleanup()