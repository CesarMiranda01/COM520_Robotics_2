import paho.mqtt.client as mqtt
import keyboard  # Library to read pressed keys

# Broker configuration
broker_ip = "192.168.222.119"  # Change to your PC's IP
topic = "orders"

# Create MQTT client
client = mqtt.Client()
client.connect(broker_ip, 1883, 60)

print("🔵 Waiting for keys... Press 'i' for left, 'd' for right.")

# Command menu with keys
while True:
    if keyboard.is_pressed('i'):  # If 'i' key is pressed
        client.publish(topic, "left")
        print("✅ Order sent: left")
        while keyboard.is_pressed('i'):  # Wait until key is released
            pass  # Maintain loop to avoid sending multiple commands
    
    elif keyboard.is_pressed('d'):  # If 'd' key is pressed
        client.publish(topic, "right")
        print("✅ Order sent: right")
        while keyboard.is_pressed('d'):  # Wait until key is released
            pass  # Maintain loop to avoid sending multiple commands

    # You can add a 'break' if you want to exit with a special key
    if keyboard.is_pressed('esc'):  # Press 'Esc' to exit the loop
        print("🚪 Exiting...")
        break

client.disconnect()