# Control de Motor Paso a Paso con Raspberry Pi y MQTT

Este proyecto demuestra cómo controlar un motor paso a paso bipolar utilizando una Raspberry Pi, un puente H L298N, y comunicación mediante el protocolo MQTT. La Raspberry Pi se suscribe a un broker MQTT (ejecutándose en un contenedor Docker) para recibir comandos desde una computadora y accionar el motor en consecuencia.

## Componentes

* **Raspberry Pi:** El cerebro del sistema, encargado de ejecutar el código Python para controlar el motor y comunicarse con el broker MQTT.
* **Puente H L298N:** Interfaz de potencia entre la Raspberry Pi y el motor paso a paso, permitiendo controlar la dirección y el flujo de corriente hacia las bobinas del motor.
* **Motor Paso a Paso Bipolar:** El dispositivo que se moverá según los comandos recibidos.
* **Computadora:** Utilizada para enviar comandos de control al motor a través del broker MQTT.
* **Broker MQTT (Mosquitto en Docker):** Un servidor de mensajería que facilita la comunicación entre la computadora y la Raspberry Pi.
* **Cables de Conexión:** Para interconectar los componentes.

## Diagrama de Conexión (Conceptual)
+-------------+         +-----------+         +-----------------+         +-------------+
| Computadora | <-------> | Broker    | <-------> | Raspberry Pi    | <-------> | Motor Paso  |
| (Publica    | (MQTT)    | (Mosquitto | (MQTT)    | (Suscriptor     | (GPIO)    | a Paso      |
| comandos)   |         | en Docker) |         | y Controlador)  |         | (L298N)     |
+-------------+         +-----------+         +-----------------+         +-------------+
## Requisitos

* **Hardware:**
    * Raspberry Pi (con GPIO habilitado)
    * Puente H L298N
    * Motor Paso a Paso Bipolar
    * Fuente de alimentación para el motor (adecuada al voltaje del motor)
    * Cables jumper para las conexiones
    * Computadora con conexión a internet (para interactuar con el broker)
* **Software:**
    * **Raspberry Pi:**
        * Raspbian (o sistema operativo similar con soporte para Python y GPIO)
        * Librería `RPi.GPIO` instalada (`sudo apt-get install python3-rpi.gpio`)
        * Librería `paho-mqtt` instalada (`pip3 install paho-mqtt`)
    * **Computadora:**
        * Python 3 instalado
        * Librería `paho-mqtt` instalada (`pip install paho-mqtt`)
        * Librería `keyboard` instalada (`pip install keyboard`)
        * Docker instalado (para ejecutar el broker Mosquitto)

## Configuración

1.  **Clonar el Repositorio (Opcional):** Si este proyecto está en un repositorio, clónalo en tu computadora y en la Raspberry Pi.

2.  **Configurar el Broker MQTT (Docker):**
    * Asegúrate de tener Docker instalado en tu computadora.
    * El archivo `docker-compose.yml` incluido define el servicio Mosquitto. Ejecuta el siguiente comando en la misma carpeta del archivo para iniciar el broker:
        ```bash
        docker-compose up -d
        ```
    * Esto creará y ejecutará un contenedor llamado `mosquitto` con los puertos necesarios mapeados. Los archivos de configuración, datos y logs del broker se montarán en las carpetas `./config`, `./data`, y `./log` respectivamente (puedes personalizarlos si es necesario).

3.  **Conectar el Motor Paso a Paso y el Puente H a la Raspberry Pi:**
    * Conecta las bobinas del motor paso a paso a las salidas del puente H (OUT1, OUT2, OUT3, OUT4). Consulta la hoja de datos de tu motor para identificar las bobinas.
    * Conecta las entradas del puente H (IN1, IN2, IN3, IN4) a los pines GPIO de la Raspberry Pi definidos en el script (`IN1 = 17`, `IN2 = 18`, `IN3 = 27`, `IN4 = 22`). **Asegúrate de usar los pines GPIO correctos.**
    * Conecta la alimentación del motor al puente H (VCC del motor y GND). **Verifica el voltaje requerido por tu motor y utiliza una fuente de alimentación adecuada.**
    * Conecta la alimentación del puente H (VCC lógica y GND) a la Raspberry Pi (normalmente 5V y GND). **Asegúrate de que los niveles de voltaje sean compatibles.**
    * Conecta los pines de habilitación (ENA, ENB) del puente H a pines GPIO PWM de la Raspberry Pi si deseas controlar la velocidad (en este script no se implementa, pero podrían conectarse a pines GPIO de salida y configurarse en alto para habilitar los puentes).

4.  **Configurar la Dirección IP del Broker:**
    * En el script de la Raspberry Pi (`motor_control.py`) y en el script de la computadora (`control_pc.py`), asegúrate de que la variable `broker_ip` coincida con la dirección IP de tu computadora donde está corriendo el contenedor Docker de Mosquitto. En los scripts proporcionados, está configurada como `192.168.222.119`. **Reemplaza esta IP con la correcta para tu red.**

5.  **Ajustar los Parámetros del Motor (Opcional):**
    * En el script `motor_control.py` de la Raspberry Pi, la variable `PASOS_90_GRADOS` está configurada en `25`. Este valor depende de las especificaciones de tu motor paso a paso (cuántos pasos necesita para una revolución completa). Ajusta este valor para lograr el movimiento deseado (por ejemplo, si tu motor da 200 pasos por revolución, para 90 grados serían 200 / 4 = 50 pasos).
    * La variable `DELAY` controla la velocidad de los pasos. Ajústala según las capacidades de tu motor.

## Ejecución

1.  **Ejecutar el Broker MQTT:** Asegúrate de que el contenedor Docker de Mosquitto esté en funcionamiento en tu computadora (`docker-compose up -d`).

2.  **Ejecutar el Script en la Raspberry Pi:** Conéctate a tu Raspberry Pi mediante SSH o un terminal y ejecuta el script de control del motor:
    ```bash
    python3 motor_control.py
    ```
    Verás el mensaje `📡 Escuchando órdenes en 'ordenes' (IP_DE_TU_COMPUTADORA)...`, indicando que la Raspberry Pi está conectada al broker y esperando comandos.

3.  **Ejecutar el Script en la Computadora:** Abre una nueva terminal en tu computadora y ejecuta el script de control:
    ```bash
    python3 control_pc.py
    ```
    Verás el mensaje `🔵 Esperando teclas... Presioná 'i' para izquierda, 'd' para derecha.`.

## Uso

Una vez que ambos scripts estén en ejecución:

* En la terminal de la computadora, presiona la tecla `'i'` para enviar el comando "izquierda" a la Raspberry Pi. El motor debería girar 90 grados en sentido antihorario (o en el sentido configurado como "izquierda" en el script de la Raspberry Pi).
* Presiona la tecla `'d'` para enviar el comando "derecha". El motor debería girar 90 grados en sentido horario (o en el sentido configurado como "derecha").
* Presiona la tecla `'Esc'` en la computadora para detener el script de control.
* Para detener el script en la Raspberry Pi, presiona `Ctrl + C` en su terminal.
