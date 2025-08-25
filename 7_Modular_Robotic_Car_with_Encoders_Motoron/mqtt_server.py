import paho.mqtt.client as mqtt
import keyboard
import time

# --- CONFIGURACIÓN ---
MQTT_BROKER_IP = "localhost"  # Usamos localhost porque el broker corre en este mismo PC
MQTT_PORT = 1883
MQTT_TOPIC_COMMANDS = "car/control"

# --- Lógica de Control ---

# Crear el cliente MQTT
client = mqtt.Client()

# Diccionario para mapear teclas a comandos
key_to_command = {
    'w': 'adelante',
    's': 'atras',
    'a': 'izquierda',
    'd': 'derecha',
    'space': 'stop' # La barra espaciadora para detener el coche
}

last_command_sent = None

def send_command(command):
    """Publica un comando en el broker MQTT."""
    global last_command_sent
    # Solo envía el comando si es diferente al último enviado
    # para evitar saturar el broker.
    if command != last_command_sent:
        print(f"Enviando comando: '{command}'")
        client.publish(MQTT_TOPIC_COMMANDS, command)
        last_command_sent = command

def on_key_press(event):
    """Callback que se ejecuta al presionar una tecla."""
    key = event.name
    if key in key_to_command:
        command = key_to_command[key]
        send_command(command)

def on_key_release(event):
    """Callback que se ejecuta al soltar una tecla."""
    # Al soltar W, A, S, o D, enviamos el comando de parada.
    key = event.name
    if key in ['w', 'a', 's', 'd']:
        print(f"Tecla '{key}' soltada, enviando 'stop'.")
        send_command('stop')

# --- Ejecución Principal ---
if __name__ == "__main__":
    try:
        print(f"Conectando al broker MQTT en {MQTT_BROKER_IP}...")
        client.connect(MQTT_BROKER_IP, MQTT_PORT, 60)
        client.loop_start() # Inicia el bucle de red en un hilo separado
        print("Conexión exitosa. El control está activo.")

        # Registrar los callbacks de teclado
        keyboard.on_press(on_key_press)
        keyboard.on_release(on_key_release)

        # Imprimir instrucciones
        print("\n--- Control del Robot ---")
        print(" W: Mover Adelante")
        print(" S: Mover Atrás")
        print(" A: Girar a la Izquierda")
        print(" D: Girar a la Derecha")
        print(" Barra Espaciadora: Parada de Emergencia")
        print("\nPresiona 'ESC' para salir del programa.")
        
        # Mantener el script corriendo hasta que se presione 'esc'
        keyboard.wait('esc')

    except Exception as e:
        print(f"Error de conexión o de teclado: {e}")
        print("Asegúrate de que el broker MQTT esté corriendo.")
        print("En Linux, puede que necesites ejecutar este script con 'sudo'.")
    finally:
        print("\nCerrando conexión y saliendo...")
        client.loop_stop()
        client.disconnect()