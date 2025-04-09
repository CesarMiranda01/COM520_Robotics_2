import RPi.GPIO as GPIO
import time

class Servo:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        self.pwm = GPIO.PWM(self.pin, 50)  # Frecuencia de 50 Hz
        self.pwm.start(0)
    
    def set_angle(self, angle, delay=0.02):
        duty_cycle = (angle / 18) + 2  # Conversin de ngulo a ciclo de trabajo
        self.pwm.ChangeDutyCycle(duty_cycle)
        time.sleep(delay)
    
    def move_to_angle(self, angle):
        """Mueve el servo directamente a un ngulo sin movimiento suave."""
        duty_cycle = (angle / 18) + 2
        self.pwm.ChangeDutyCycle(duty_cycle)
        time.sleep(0.5)  # Espera para asegurar el movimiento
        self.pwm.ChangeDutyCycle(0)  # Detiene el PWM para evitar vibraciones
    
    def smooth_move(self, start_angle, end_angle, step=1, delay=0.02):
        step = step if start_angle < end_angle else -step
        for angle in range(start_angle, end_angle + step, step):
            self.set_angle(angle, delay)
        self.pwm.ChangeDutyCycle(0)  # Detener el pulso PWM despus del movimiento
    
    def cleanup(self):
        self.pwm.stop()
        GPIO.cleanup()
