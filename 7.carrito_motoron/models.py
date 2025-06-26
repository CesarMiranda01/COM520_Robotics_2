# models.py
# El modelo final para el robot real. Incluye Gain Scheduling y Compensación de Zona Muerta.

import time
import threading
import RPi.GPIO as GPIO
import motoron

class Encoder:
    """Maneja la lectura de un encoder de cuadratura usando interrupciones GPIO."""
    def __init__(self, pin_a, pin_b):
        self.pin_a, self.pin_b = pin_a, pin_b
        self.position = 0
        self.lock = threading.Lock()
        GPIO.setup(self.pin_a, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.pin_b, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.pin_a, GPIO.RISING, callback=self._callback)

    def _callback(self, channel):
        with self.lock:
            if GPIO.input(self.pin_b): self.position += 1
            else: self.position -= 1

    def get_position(self):
        with self.lock: return self.position

class MotorPID:
    """Controlador PID avanzado con Gain Scheduling y Compensación de Zona Muerta."""
    ## MODIFICADO ## - Añadido 'min_power_to_move' para la compensación.
    def __init__(self, motoron_controller, motor_id, encoder_a, encoder_b, 
                 pid_schedule, min_power_to_move=0, scale_factor=1.0):
        self.mc = motoron_controller
        self.motor_id = motor_id
        self.encoder = Encoder(encoder_a, encoder_b)
        self.scale_factor = scale_factor
        
        self.gain_schedule = pid_schedule
        self.min_power_to_move = int(min_power_to_move * self.scale_factor) # <-- NUEVO: Guarda la potencia mínima, escalada.
        self.speed_zones = {}
        
        self.Kp, self.Ki, self.Kd = 0, 0, 0
        self.target_speed_tps, self.current_speed_tps = 0.0, 0.0
        self._last_pos, self._last_time = 0, time.time()
        self._integral, self._prev_err = 0.0, 0.0
        self._speed_command = 0
        
        self.MAX_POWER = int(800 * self.scale_factor)
        self.MIN_POWER = int(-800 * self.scale_factor)

    def set_speed_zones(self, zones):
        self.speed_zones = zones

    def set_target_speed(self, speed):
        self._integral = 0
        self.target_speed_tps = speed
        
        abs_speed = abs(self.target_speed_tps)
        if abs_speed > self.speed_zones.get('high_threshold', float('inf')):
            active_gains = self.gain_schedule.get('high')
        elif abs_speed > self.speed_zones.get('mid_threshold', float('inf')):
            active_gains = self.gain_schedule.get('mid')
        else:
            active_gains = self.gain_schedule.get('low')
        
        if active_gains: self.Kp, self.Ki, self.Kd = active_gains

    def update(self):
        now = time.time(); dt = now - self._last_time
        if dt < 0.001: return
        self._last_time = now
        
        pos = self.encoder.get_position()
        self.current_speed_tps = (pos - self._last_pos) / dt
        self._last_pos = pos
        
        # Si el objetivo es cero, paramos y reseteamos todo. Es más robusto.
        if abs(self.target_speed_tps) < 0.01:
            self.stop()
            return
            
        err = self.target_speed_tps - self.current_speed_tps
        
        p = self.Kp * err
        self._integral = max(min(self._integral + err * dt, 200), -200)
        i = self.Ki * self._integral
        # Usar la velocidad actual para el derivativo (Derivative on Measurement) es más estable
        d = -self.Kd * (self.current_speed_tps - self._prev_err) / dt if dt > 0 else 0
        self._prev_err = self.current_speed_tps
        
        pid_output = p + i + d
        
        ## MODIFICADO ## - Lógica de Compensación de Zona Muerta (Feedforward)
        final_command = 0
        if self.target_speed_tps > 0:
            final_command = self.min_power_to_move + pid_output
        elif self.target_speed_tps < 0:
            final_command = -self.min_power_to_move + pid_output
        
        self._speed_command = max(min(final_command, self.MAX_POWER), self.MIN_POWER)
        
        self.mc.set_speed(self.motor_id, int(self._speed_command))

    def stop(self):
        self.target_speed_tps = 0; self._speed_command = 0
        self.mc.set_speed(self.motor_id, 0)

class RobotController:
    """Orquesta todos los motores del robot real."""
    def __init__(self, config):
        self.config = config
        self.motors = {}
        self._running = False
        self._control_thread = None

        GPIO.setmode(GPIO.BCM)
        self.mc_left = motoron.MotoronI2C(address=config['MOTORON_ADDR_LEFT'])
        self.mc_right = motoron.MotoronI2C(address=config['MOTORON_ADDR_RIGHT'])
        
        for mc in [self.mc_left, self.mc_right]: mc.reinitialize(); mc.clear_reset_flag()

        max_speed = config['ROBOT_GLOBAL_MAX_SPEED']
        zones = {'mid_threshold': max_speed * 0.4, 'high_threshold': max_speed * 0.7}

        for name, cfg in config['MOTORS'].items():
            mc = self.mc_left if cfg['controller'] == 'left' else self.mc_right
            self.motors[name] = MotorPID(
                motoron_controller=mc, motor_id=cfg['id'],
                encoder_a=cfg['encoder_a'], encoder_b=cfg['encoder_b'],
                pid_schedule=cfg['pid_schedule'], 
                min_power_to_move=cfg.get('min_power', 0), # <-- USA EL NUEVO VALOR
                scale_factor=cfg.get('scale_factor', 1.0)
            )
            self.motors[name].set_speed_zones(zones)

    def start(self):
        if not self._running:
            self._running = True
            self._control_thread = threading.Thread(target=self._run_pid_loop, daemon=True)
            self._control_thread.start()

    def _run_pid_loop(self):
        while self._running:
            for motor in self.motors.values():
                motor.update()
            time.sleep(self.config['PID_LOOP_DELAY'])

    def move_forward(self, percent):
        target_tps = self.config['ROBOT_GLOBAL_MAX_SPEED'] * (percent / 100.0)
        for motor in self.motors.values(): motor.set_target_speed(target_tps)

    def turn_right_pivot(self, percent):
        target_tps = self.config['ROBOT_GLOBAL_MAX_SPEED'] * (percent / 100.0)
        for name, motor in self.motors.items():
            if name.endswith('r'): motor.set_target_speed(-target_tps)
            else: motor.set_target_speed(target_tps)

    def stop(self):
        for motor in self.motors.values(): motor.stop()
        
    def cleanup(self):
        if self._running: self._running = False; self._control_thread.join(timeout=1.0)
        self.stop()
        GPIO.cleanup()