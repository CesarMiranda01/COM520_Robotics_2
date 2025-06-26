import paho.mqtt.client as mqtt
import time
import json
import atexit
from models import RobotController


# --- CONFIGURACIÓN ---
# Dirección IP del PC que ejecuta el broker MQTT (Docker)
MQTT_BROKER_IP = "192.168.146.119"  # <--- ¡CAMBIA ESTO por la IP de tu PC!
MQTT_PORT = 1883
MQTT_TOPIC_COMMANDS = "car/control"

# Velocidad de movimiento del robot (en porcentaje). Ajústala a tu gusto.
MOVEMENT_SPEED_PERCENT = 50.0

ROBOT_CONFIG = {
    # Direcciones I2C de las controladoras Motoron (de tuner.py)
    "MOTORON_ADDR_LEFT": 16,
    "MOTORON_ADDR_RIGHT": 17,
    "PID_LOOP_DELAY": 0.02,

    # ¡ADVERTENCIA! El siguiente valor es un Platzhalter.
    # El `tuner.py` calculará el valor correcto para tu robot.
    "ROBOT_GLOBAL_MAX_SPEED": 4200.0,

    "MOTORS": {
        # --- Motor Frontal Izquierdo (fl) ---
        "fl": {
            "controller": "left",  # Agrupación lógica de main.py
            "id": 2,               # ID de motoron de tuner.py
            "encoder_a": 5,        # Pin A de tuner.py
            "encoder_b": 6,        # Pin B de tuner.py
            # ¡ADVERTENCIA! Valores de PID de ejemplo. Usa los generados por tuner.py
            "pid_schedule": {
                "low":  [0.105, 0.449, 0.000],
                "mid":  [0.095, 0.408, 0.000],
                "high": [0.086, 0.408, 0.000]
            },
            "min_power": 42,
            "scale_factor": 0.9811
        },
        # --- Motor Trasero Izquierdo (bl) ---
        "bl": {
            "controller": "right",  # Agrupación lógica de main.py
            "id": 3,               # ID de motoron de tuner.py
            "encoder_a": 19,       # Pin A de tuner.py (Ojo: en tuner es 19,13)
            "encoder_b": 13,       # Pin B de tuner.py
            # ¡ADVERTENCIA! Valores de PID de ejemplo. Usa los generados por tuner.py
            "pid_schedule": {
                "low":  [0.108, 0.461, 0.000],
                "mid":  [0.098, 0.419, 0.000],
                "high": [0.088, 0.419, 0.000]
            },
            "min_power": 40,
            "scale_factor": 0.9698
        },
        # --- Motor Frontal Derecho (fr) ---
        "fr": {
            "controller": "left", # Agrupación lógica de main.py
            "id": 3,               # ID de motoron de tuner.py
            "encoder_a": 26,       # Pin A de tuner.py
            "encoder_b": 12,       # Pin B de tuner.py
            # ¡ADVERTENCIA! Valores de PID de ejemplo. Usa los generados por tuner.py
            "pid_schedule": {
                "low":  [0.102, 0.435, 0.000],
                "mid":  [0.093, 0.395, 0.000],
                "high": [0.083, 0.395, 0.000]
            },
            "min_power": 44,
            "scale_factor": 1.0
        },
        # --- Motor Trasero Derecho (br) ---
        "br": {
            "controller": "right", # Agrupación lógica de main.py
            "id": 2,               # ID de motoron de tuner.py
            "encoder_a": 16,       # Pin A de tuner.py
            "encoder_b": 20,       # Pin B de tuner.py
            # ¡ADVERTENCIA! Valores de PID de ejemplo. Usa los generados por tuner.py
            "pid_schedule": {
                "low":  [0.104, 0.443, 0.000],
                "mid":  [0.094, 0.403, 0.000],
                "high": [0.085, 0.403, 0.000]
            },
            "min_power": 42,
            "scale_factor": 0.9904
        }
    }
}


# --- Lógica de Control del Robot ---

# Inicializa el controlador del robot con nuestra configuración
print("Inicializando el controlador del robot...")
controller = RobotController(ROBOT_CONFIG)
controller.start() # Inicia el bucle PID en segundo plano (importante para el watchdog)
print("Controlador del robot listo.")

# Nos aseguramos de que los motores se paren y los recursos se liberen al salir
@atexit.register
def cleanup():
    print("Deteniendo el robot y limpiando recursos...")
    if controller:
        controller.cleanup()
    print("Limpieza completa.")

# --- Funciones de Movimiento ---

def move_forward(speed_percent):
    print(f"Comando: Mover adelante al {speed_percent}%")
    controller.move_forward(speed_percent)

def move_backward(speed_percent):
    print(f"Comando: Mover atrás al {speed_percent}%")
    controller.move_forward(-speed_percent) # move_forward con valor negativo

def turn_left(speed_percent):
    print(f"Comando: Girar a la izquierda al {speed_percent}%")
    target_tps = ROBOT_CONFIG['ROBOT_GLOBAL_MAX_SPEED'] * (speed_percent / 100.0)
    # Ruedas derechas hacia adelante, ruedas izquierdas hacia atrás
    for name, motor in controller.motors.items():
        if name.endswith('r'):
            motor.set_target_speed(target_tps)
        else: # 'l'
            motor.set_target_speed(-target_tps)

def turn_right(speed_percent):
    print(f"Comando: Girar a la derecha al {speed_percent}%")
    # Usamos la función ya definida en models.py
    controller.turn_right_pivot(speed_percent)

def stop_all_motors():
    print("Comando: Parada de emergencia")
    controller.stop()

# --- Lógica MQTT ---

# Callback que se ejecuta cuando nos conectamos al broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Conectado exitosamente al broker MQTT.")
        client.subscribe(MQTT_TOPIC_COMMANDS)
        print(f"Suscrito al tópico: {MQTT_TOPIC_COMMANDS}")
    else:
        print(f"Fallo al conectar, código de error: {rc}")

# Callback que se ejecuta cuando llega un mensaje
def on_message(client, userdata, msg):
    command = msg.payload.decode()
    
    if command == "adelante":
        move_forward(MOVEMENT_SPEED_PERCENT)
    elif command == "atras":
        move_backward(MOVEMENT_SPEED_PERCENT)
    elif command == "izquierda":
        turn_left(MOVEMENT_SPEED_PERCENT)
    elif command == "derecha":
        turn_right(MOVEMENT_SPEED_PERCENT)
    elif command == "stop":
        stop_all_motors()
    else:
        print(f"Comando desconocido recibido: {command}")

# --- Ejecución Principal ---
if __name__ == "__main__":
    controller = None
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        # 1. Inicializar el hardware DENTRO del bloque 'try'
        print("Inicializando el controlador del robot...")
        controller = RobotController(ROBOT_CONFIG)
        controller.start()
        print("Controlador del robot listo.")

        # 2. Conectar al broker MQTT
        print(f"Intentando conectar al broker en {MQTT_BROKER_IP}...")
        client.connect(MQTT_BROKER_IP, MQTT_PORT, 60)

        # 3. Iniciar el bucle de escucha de MQTT.
        #    Esto es un bucle bloqueante. El script se quedará aquí
        #    hasta que lo detengas con Ctrl+C.
        client.loop_forever()

    except KeyboardInterrupt:
        print("\nPrograma detenido por el usuario.")
    except RuntimeError as e:
        # Capturamos el error específico de GPIO para dar un mensaje más útil
        print(f"\nERROR DE HARDWARE (GPIO): {e}")
        print("Este error suele ocurrir porque un pin no se liberó correctamente.")
        print("Intenta reiniciar la Raspberry Pi. Si el problema continúa, verifica que los pines definidos en ROBOT_CONFIG no estén siendo usados por otros servicios (como SPI, 1-Wire, etc.).")
    except Exception as e:
        # Capturamos cualquier otro error inesperado
        print(f"\nOcurrió un error inesperado: {e}")
    finally:
        # 4. El bloque 'finally' se ejecuta SIEMPRE:
        #    - Si el script termina normalmente.
        #    - Si se interrumpe con Ctrl+C.
        #    - Si ocurre cualquier otro error (¡incluido el tuyo!).
        print("\nIniciando secuencia de limpieza final...")
        if client.is_connected():
            client.loop_stop()
            client.disconnect()
            print("Cliente MQTT desconectado.")

        if controller:
            # Si el controlador se inicializó, usamos su método de limpieza
            controller.cleanup()
            print("Limpieza del controlador finalizada.")
        else:
            # Si el controlador falló al inicializarse (como en tu caso),
            # no podemos llamar a controller.cleanup(), pero podemos intentar
            # una limpieza general de GPIO por si acaso.
            print("El controlador no se inicializó. Intentando limpieza general de GPIO.")
            import RPi.GPIO as GPIO
            GPIO.cleanup()
        print("Script finalizado.")