
import time
import threading
import random
import sys
import collections
import matplotlib.pyplot as plt

print("\n" + "="*60)
print("--- BANCO DE PRUEBAS PID CON GRÁFICOS (vFinal) ---")
print("="*60)


class SimulatedMotor:
    def __init__(self, name):
        self.name = name
        self.max_acceleration = random.uniform(8000, 12000)
        self.friction_coeff = random.uniform(8, 12)
        self.power, self.velocity, self.position = 0.0, 0.0, 0.0
    def set_power(self, power): self.power = float(power)
    def update(self, delta_time):
        friction = self.velocity * self.friction_coeff
        accel = (self.power / 800.0 * self.max_acceleration) - friction
        self.velocity += accel * delta_time
        self.position += self.velocity * delta_time
    def get_encoder_position(self): return int(self.position)

class SimulatedEncoder:
    def __init__(self, sim_motor): self.sim_motor = sim_motor
    def get_position(self): return self.sim_motor.get_encoder_position()

class SimulatedMotorPID:
    def __init__(self, motor_key):
        self.motor = simulated_motors[motor_key]
        self.encoder = SimulatedEncoder(self.motor)
        self.gain_schedule = {}
        self.speed_zones = {}
        self.Kp, self.Ki, self.Kd = 0, 0, 0
        self.target_speed_tps = 0.0
        self.current_speed_tps = 0.0
        self._last_pos = 0
        self._last_time = time.time()
        self._integral = 0.0
        self.output = 0.0
        self.speed_buffer = collections.deque(maxlen=5)
        self.anti_windup_tracking_gain = 0.1

    def set_gain_schedule(self, schedule, zones):
        self.gain_schedule = schedule
        self.speed_zones = zones

    def set_target_speed(self, speed):
        self._integral = 0.0
        self.target_speed_tps = speed
        current_gains_name = "low"
        if self.gain_schedule:
             abs_speed = abs(self.target_speed_tps)
             if abs_speed > self.speed_zones.get('high', float('inf')): current_gains_name = "high"
             elif abs_speed > self.speed_zones.get('mid', float('inf')): current_gains_name = "mid"
             else: current_gains_name = "low"
             self.Kp, self.Ki, self.Kd = self.gain_schedule.get(current_gains_name, (0,0,0))
        return current_gains_name

    def update(self):
        now = time.time()
        dt = now - self._last_time
        if dt < 0.001: return
        last_filtered_speed = self.current_speed_tps
        self._last_time = now
        pos = self.encoder.get_position()
        raw_speed = (pos - self._last_pos) / dt if dt > 0 else 0
        self.speed_buffer.append(raw_speed)
        self.current_speed_tps = sum(self.speed_buffer) / len(self.speed_buffer)
        self._last_pos = pos
        err = self.target_speed_tps - self.current_speed_tps
        p_out = self.Kp * err
        derivative = (self.current_speed_tps - last_filtered_speed) / dt if dt > 0 else 0
        d_out = -self.Kd * derivative
        pre_output = p_out + self._integral + d_out
        self.output = max(min(pre_output, 800), -800)
        self._integral += self.Ki * err * dt
        windup_error = self.output - pre_output
        self._integral += self.anti_windup_tracking_gain * windup_error
        self.motor.set_power(self.output)

    def stop(self):
        self.target_speed_tps, self.output = 0, 0
        self._integral = 0
        self.motor.set_power(0)

simulated_motors = {}
_sim_running = True
def physics_loop():
    last_time = time.time()
    while _sim_running:
        now = time.time()
        dt = now - last_time
        last_time = now
        for motor in simulated_motors.values():
            motor.update(dt)
        time.sleep(0.001)

def get_float_input(prompt, default=None):
    while True:
        try:
            val = input(prompt)
            if val == "" and default is not None: return default
            return float(val)
        except (ValueError, TypeError): print("Entrada no válida.")
        except KeyboardInterrupt: raise

def tune_with_step_response(pid_controller):
    print("\n--- INICIANDO CALIBRACIÓN POR RESPUESTA AL ESCALÓN (Lambda Tuning) ---")
    print("  -> Aplicando escalón de potencia y registrando datos...")
    pid_controller.stop()
    input_power = 800.0
    pid_controller.motor.set_power(input_power)
    history = []
    start_time = time.time()
    pid_controller._last_pos = pid_controller.encoder.get_position()
    pid_controller._last_time = start_time
    pid_controller.speed_buffer.clear()
    pid_controller.current_speed_tps = 0.0
    while time.time() - start_time < 4.0:
        now = time.time()
        dt = now - pid_controller._last_time
        if dt > 0.005:
            pid_controller._last_time = now
            pos = pid_controller.encoder.get_position()
            raw_speed = (pos - pid_controller._last_pos) / dt
            pid_controller._last_pos = pos
            pid_controller.speed_buffer.append(raw_speed)
            pid_controller.current_speed_tps = sum(pid_controller.speed_buffer) / len(pid_controller.speed_buffer)
        history.append((time.time() - start_time, pid_controller.current_speed_tps))
        sys.stdout.write(f"\r     Tiempo: {history[-1][0]:.2f}s, Velocidad: {history[-1][1]:.1f} Ticks/s")
        sys.stdout.flush()
        time.sleep(0.01)
    pid_controller.stop()
    print("\n  -> Análisis de la respuesta...")
    max_speed = history[-1][1]
    if max_speed < 1:
        print("     ¡Error! El motor no se movió.")
        return None, None
    K_process = max_speed / input_power
    L = 0
    for t, speed in history:
        if speed > max_speed * 0.05:
            L = t
            break
    tau_target_speed = max_speed * 0.632
    t_at_63_percent = 0
    for t, speed in history:
        if speed >= tau_target_speed:
            t_at_63_percent = t
            break
    tau = t_at_63_percent - L
    if tau <= 0:
        print(f"     ¡Error! No se pudo calcular Tau (Tau={tau:.3f}).")
        return None, None
    print(f"     Parámetros del modelo: K_process={K_process:.3f}, L={L:.3f}s, Tau={tau:.3f}s")
    print("  -> Calculando ganancias PID con Lambda Tuning...")
    lmbda = tau 
    kp = tau / (K_process * (lmbda + L))
    Ti = tau
    Td = 0
    ki = kp / Ti if Ti > 0 else 0
    kd = kp * Td
    final_gains = {'low': (kp, ki, kd), 'mid': (kp, ki, kd), 'high': (kp, ki, kd)}
    print(f"     Valores PID calculados: Kp={kp:.4f}, Ki={ki:.4f}, Kd={kd:.4f}")
    return final_gains, max_speed

def manual_tune(pid_controller, max_speed):
    # (Sin cambios)
    print("\n--- MODO DE AFINACIÓN MANUAL ---")
    target_percent = 50.0
    active_gains = "low"
    if max_speed > 0:
        pid_controller.set_target_speed(max_speed * (target_percent / 100.0))
    while True:
        pid_controller.update()
        actual, target = pid_controller.current_speed_tps, pid_controller.target_speed_tps
        kp, ki, kd = pid_controller.Kp, pid_controller.Ki, pid_controller.Kd
        sys.stdout.write("\r" + " "*100 + "\r")
        sys.stdout.write(f"Kp={kp:<6.4f} Ki={ki:<6.4f} Kd={kd:<6.4f} | Gains: {active_gains.upper():<4s} | Target={target:<7.1f} Actual={actual:<7.1f}")
        sys.stdout.flush()
        time.sleep(0.1)
        print("\nComandos: [s]et speed, [p] Kp, [i] Ki, [d] Kd, [q]uit manual tune")
        choice = input("> ").lower()
        if choice == 'q':
            print(f"\nValores finales: Kp={pid_controller.Kp:.4f}, Ki={pid_controller.Ki:.4f}, Kd={pid_controller.Kd:.4f}")
            break
        elif choice == 's':
            target_percent = get_float_input(f"Nuevo % ({target_percent}): ", target_percent)
            if max_speed > 0: active_gains = pid_controller.set_target_speed(max_speed * (target_percent / 100.0))
        elif choice == 'p': pid_controller.Kp = get_float_input(f"Nuevo Kp ({pid_controller.Kp}): ", pid_controller.Kp)
        elif choice == 'i': pid_controller.Ki = get_float_input(f"Nuevo Ki ({pid_controller.Ki}): ", pid_controller.Ki)
        elif choice == 'd': pid_controller.Kd = get_float_input(f"Nuevo Kd ({pid_controller.Kd}): ", pid_controller.Kd)

## MODIFICADO ## - Ahora recolecta y retorna los datos para el gráfico
def test_drive(pid_controller, max_speed):
    print("\n\n--- INICIANDO TEST DRIVE ---")
    plot_data = []
    test_speeds = [0, 25, 50, 85, 50, 25, 0]
    total_start_time = time.time()
    
    for percent in test_speeds:
        target_speed = max_speed * (percent / 100.0)
        active_gains_name = pid_controller.set_target_speed(target_speed)
        print(f"\nCambiando a {percent}% velocidad. GAINS ACTIVOS: [{active_gains_name.upper()}]")
        
        start_time = time.time()
        while time.time() - start_time < 3.0:
            pid_controller.update()
            actual, target = pid_controller.current_speed_tps, pid_controller.target_speed_tps
            
            # Recolectar datos para el gráfico
            current_time = time.time() - total_start_time
            plot_data.append({'time': current_time, 'target': target, 'actual': actual})
            
            sys.stdout.write(f"\r  Target={target:<7.1f} Actual={actual:<7.1f} | Kp={pid_controller.Kp:.3f}, Ki={pid_controller.Ki:.3f}, Kd={pid_controller.Kd:.3f}")
            sys.stdout.flush()
            time.sleep(0.02)
            
    pid_controller.stop()
    print("\nTest Drive finalizado.")
    return plot_data

## NUEVO ## - Función para crear y mostrar el gráfico
def plot_results(data):
    """
    Toma los datos recolectados y genera un gráfico de rendimiento del PID.
    """
    if not data:
        print("\nNo hay datos para graficar.")
        return

    print("\nGenerando gráfico de rendimiento...")
    
    # Extraer los datos en listas separadas
    times = [d['time'] for d in data]
    targets = [d['target'] for d in data]
    actuals = [d['actual'] for d in data]

    # Crear la figura y los ejes para el gráfico
    plt.figure(figsize=(12, 7))
    plt.plot(times, targets, '--', label='Velocidad Objetivo (Setpoint)', color='gray', linewidth=2)
    plt.plot(times, actuals, '-', label='Velocidad Real (Medida)', color='dodgerblue', linewidth=2.5)

    # Añadir títulos, etiquetas y leyenda para que sea legible
    plt.title('Rendimiento del Controlador PID en el Test Drive', fontsize=16)
    plt.xlabel('Tiempo (segundos)', fontsize=12)
    plt.ylabel('Velocidad (Ticks/s)', fontsize=12)
    plt.legend(fontsize=11)
    plt.grid(True, which='both', linestyle=':', linewidth=0.5)
    plt.ylim(min(targets) - 100, max(targets) + 100) # Ajustar límites del eje Y para mejor visualización
    
    # Mostrar el gráfico en una nueva ventana
    plt.show()

if __name__ == "__main__":
    for name in ['fl','bl','fr','br']:
        simulated_motors[name] = SimulatedMotor(name)
    physics_thread = threading.Thread(target=physics_loop, daemon=True)
    physics_thread.start()
    try:
        while True:
            print("\n" + "="*50)
            print("--- BANCO DE PRUEBAS PID (vFinal con Gráficos) ---")
            print("1. Ejecutar Auto-Calibración (Método Definitivo)")
            print("2. Ir directamente a Calibración Manual")
            print("3. Salir")
            main_choice = input("Elige una opción: ")
            if main_choice == '3': break
            if main_choice not in ['1', '2']: continue
            
            motor_name = ""
            while motor_name not in simulated_motors:
                motor_name = input(f"¿Qué motor quieres usar? {list(simulated_motors.keys())}: ").lower()

            pid_controller = SimulatedMotorPID(motor_name)
            
            if main_choice == '1':
                final_schedule, max_speed = tune_with_step_response(pid_controller)
                
                if final_schedule:
                    print("\n\n--- HORARIO DE GANANCIAS FINAL GENERADO ---")
                    zones = {'mid': max_speed * 0.45, 'high': max_speed * 0.75}
                    pid_controller.set_gain_schedule(final_schedule, zones)
                    gains = list(final_schedule.values())[0]
                    print(f"Valores para todas las zonas: Kp={gains[0]:.4f}, Ki={gains[1]:.4f}, Kd={gains[2]:.4f}")
                    
                    if input("\n¿Ejecutar 'Test Drive' con estos valores? (y/n): ").lower() == 'y':
                        ## MODIFICADO ## - Capturar los datos del Test Drive y luego graficarlos
                        collected_data = test_drive(pid_controller, max_speed)
                        plot_results(collected_data)
                        
                    if input("\n¿Afinar manualmente estos valores ahora? (y/n): ").lower() == 'y':
                        manual_tune(pid_controller, max_speed)
                else:
                    print("\nNo se pudo generar un horario de ganancias.")
            
            elif main_choice == '2':
                print("\nMidiendo la velocidad máxima del motor...")
                pid_controller.motor.set_power(800)
                time.sleep(2)
                max_speed_manual = pid_controller.motor.velocity
                pid_controller.stop()
                print(f"Velocidad máxima aprox. para modo manual: {max_speed_manual:.2f} Ticks/Sec")
                manual_tune(pid_controller, max_speed_manual)

    except KeyboardInterrupt: print("\nProceso interrumpido.")
    except Exception as e: print(f"\nError inesperado: {e}")
    finally:
        _sim_running = False
        print("\nSimulación finalizada.")