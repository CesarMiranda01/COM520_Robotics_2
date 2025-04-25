import paho.mqtt.client as mqtt
import keyboard  # Librería para leer las teclas presionadas

# Configuración del broker
broker_ip = "192.168.222.119"  # Cambiá por la IP de tu PC
topic = "ordenes"

# Crear el cliente MQTT
client = mqtt.Client()
client.connect(broker_ip, 1883, 60)

print("🔵 Esperando teclas... Presioná 'i' para izquierda, 'd' para derecha.")

# Menú de órdenes con teclas
while True:
    if keyboard.is_pressed('i'):  # Si se presiona la tecla 'i'
        client.publish(topic, "izquierda")
        print("✅ Orden enviada: izquierda")
        while keyboard.is_pressed('i'):  # Esperar hasta que se deje de presionar
            pass  # Mantener el ciclo para no enviar varias veces la misma orden
    
    elif keyboard.is_pressed('d'):  # Si se presiona la tecla 'd'
        client.publish(topic, "derecha")
        print("✅ Orden enviada: derecha")
        while keyboard.is_pressed('d'):  # Esperar hasta que se deje de presionar
            pass  # Mantener el ciclo para no enviar varias veces la misma orden

    # Podés agregar un 'break' si querés terminar el programa con una tecla especial
    if keyboard.is_pressed('esc'):  # Si presionás 'Esc', sale del loop
        print("🚪 Saliendo...")
        break

client.disconnect()
