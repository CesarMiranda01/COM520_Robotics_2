import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time

# GPIO pins connected to H-Bridge (L298N)
IN1 = 17  # Coil A
IN2 = 18
IN3 = 27  # Coil B
IN4 = 22

# GPIO configuration
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)

# Sequence for bipolar stepper motor (full step)
sequence = [
    [1, 0, 1, 0],  # A+ B+
    [0, 1, 1, 0],  # A- B+
    [0, 1, 0, 1],  # A- B-
    [1, 0, 0, 1],  # A+ B-
]

# Adjust according to your motor
STEPS_90_DEGREES = 25  # 1/4 turn = 90°
DELAY = 0.01

def move_motor(direction='right', steps=STEPS_90_DEGREES, delay=DELAY):
    motor_sequence = sequence if direction == 'right' else sequence[::-1]
    for _ in range(steps):
        for step in motor_sequence:
            GPIO.output(IN1, step[0])
            GPIO.output(IN2, step[1])
            GPIO.output(IN3, step[2])
            GPIO.output(IN4, step[3])
            time.sleep(delay)
    
    # Turn off coils when finished
    GPIO.output(IN1, 0)
    GPIO.output(IN2, 0)
    GPIO.output(IN3, 0)
    GPIO.output(IN4, 0)

# Command functions
def left():
    print("🔄 Rotating 90° to the left")
    move_motor('left')

def right():
    print("🔄 Rotating 90° to the right")
    move_motor('right')

# MQTT callback
def on_message(client, userdata, msg):
    payload = msg.payload.decode('utf-8')
    print(f"📩 Message received on '{msg.topic}': {payload}")

    if payload == "left":
        left()
    elif payload == "right":
        right()
    else:
        print("⚠️ Unknown command:", payload)

# MQTT client configuration
broker_ip = "192.168.222.119"  # Change this if your broker has a different IP
topic = "orders"

client = mqtt.Client()
client.connect(broker_ip, 1883, 60)
client.subscribe(topic)
client.on_message = on_message

print(f"📡 Listening for commands on '{topic}' ({broker_ip})...")

# Main loop
try:
    client.loop_forever()
finally:
    GPIO.cleanup()