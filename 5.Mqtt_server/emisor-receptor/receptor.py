import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time

# Pines GPIO conectados al puente H (L298N)
IN1 = 17  # Bobina A
IN2 = 18
IN3 = 27  # Bobina B
IN4 = 22

# Configuración GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)

# Secuencia para motor bipolar (paso completo)
secuencia = [
    [1, 0, 1, 0],  # A+ B+
    [0, 1, 1, 0],  # A- B+
    [0, 1, 0, 1],  # A- B-
    [1, 0, 0, 1],  # A+ B-
]

# Ajusta esto según tu motor
PASOS_90_GRADOS = 25  # 1/4 de vuelta = 90°
DELAY = 0.01

def mover_motor(sentido='derecha', pasos=PASOS_90_GRADOS, delay=DELAY):
    secuencia_motor = secuencia if sentido == 'derecha' else secuencia[::-1]
    for _ in range(pasos):
        for paso in secuencia_motor:
            GPIO.output(IN1, paso[0])
            GPIO.output(IN2, paso[1])
            GPIO.output(IN3, paso[2])
            GPIO.output(IN4, paso[3])
            time.sleep(delay)
    
    # Apagar bobinas al terminar
    GPIO.output(IN1, 0)
    GPIO.output(IN2, 0)
    GPIO.output(IN3, 0)
    GPIO.output(IN4, 0)

# Funciones para órdenes
def izquierda():
    print("🔄 Girando 90° a la izquierda")
    mover_motor('izquierda')

def derecha():
    print("🔄 Girando 90° a la derecha")
    mover_motor('derecha')

# Callback MQTT
def on_message(client, userdata, msg):
    payload = msg.payload.decode('utf-8')
    print(f"📩 Mensaje recibido en '{msg.topic}': {payload}")

    if payload == "izquierda":
        izquierda()
    elif payload == "derecha":
        derecha()
    else:
        print("⚠️ Orden desconocida:", payload)

# Configuración del cliente MQTT
broker_ip = "192.168.222.119"  # Cambia esto si tu broker está en otra IP
topic = "ordenes"

client = mqtt.Client()
client.connect(broker_ip, 1883, 60)
client.subscribe(topic)
client.on_message = on_message

print(f"📡 Escuchando órdenes en '{topic}' ({broker_ip})...")

# Bucle principal
try:
    client.loop_forever()
finally:
    GPIO.cleanup()
