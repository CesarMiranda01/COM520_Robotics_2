# Stepper Motor Control with Raspberry Pi and MQTT

This project demonstrates how to control a bipolar stepper motor using a Raspberry Pi, an L298N H-bridge, and communication through the MQTT protocol. The Raspberry Pi subscribes to an MQTT broker (running in a Docker container) to receive commands from a computer and actuate the motor accordingly.

## Components

* **Raspberry Pi:** The brain of the system, responsible for running the Python code to control the motor and communicate with the MQTT broker.
* **L298N H-Bridge:** Power interface between the Raspberry Pi and the stepper motor, allowing control of the direction and current flow to the motor coils.
* **Bipolar Stepper Motor:** The device that will move according to the received commands.
* **Computer:** Used to send control commands to the motor via the MQTT broker.
* **MQTT Broker (Mosquitto in Docker):** A messaging server that facilitates communication between the computer and the Raspberry Pi.
* **Connection Cables:** To interconnect the components.

## Connection Diagram (Conceptual)

    |   Computer  | <------->   Broker  | <------->   Raspberry Pi   | <------->   Stepper   |
    | (Publisher) |   (MQTT)  | (Docker) |   (MQTT)  | (Subscriber &  |   (GPIO)  |  Motor    |
    |  Commands   |           | Mosquitto|           |   Controller)  |           |  (L298N)  |

## Requirements

* **Hardware:**
    * Raspberry Pi (with GPIO enabled)
    * L298N H-Bridge
    * Bipolar Stepper Motor
    * Power supply for the motor (appropriate for motor voltage)
    * Jumper wires for connections
    * Computer with internet connection (to interact with the broker)
* **Software:**
    * **Raspberry Pi:**
        * Raspbian (or similar OS with Python and GPIO support)
        * `RPi.GPIO` library installed (`sudo apt-get install python3-rpi.gpio`)
        * `paho-mqtt` library installed (`pip3 install paho-mqtt`)
    * **Computer:**
        * Python 3 installed
        * `paho-mqtt` library installed (`pip install paho-mqtt`)
        * `keyboard` library installed (`pip install keyboard`)
        * Docker installed (to run the Mosquitto broker)

## Setup

1. **Clone the Repository (Optional):** If this project is in a repository, clone it to your computer and to the Raspberry Pi.

2. **Configure the MQTT Broker (Docker):**
    * Ensure Docker is installed on your computer.
    * The included `docker-compose.yml` file defines the Mosquitto service. Run the following command in the same folder as the file to start the broker:
        ```bash
        docker-compose up -d
        ```
    * This will create and run a container named `mosquitto` with the necessary ports mapped. The configuration, data, and log files of the broker will be mounted in the `./config`, `./data`, and `./log` folders respectively (you can customize these if needed).

3. **Connect the Stepper Motor and H-Bridge to the Raspberry Pi:**
    * Connect the stepper motor coils to the H-Bridge outputs (OUT1, OUT2, OUT3, OUT4). Refer to your motor’s datasheet to identify the coils.
    * Connect the H-Bridge inputs (IN1, IN2, IN3, IN4) to the Raspberry Pi GPIO pins defined in the script (`IN1 = 17`, `IN2 = 18`, `IN3 = 27`, `IN4 = 22`). **Make sure to use the correct GPIO pins.**
    * Connect the motor power supply to the H-Bridge (motor VCC and GND). **Check the required voltage for your motor and use an appropriate power supply.**
    * Connect the H-Bridge logic power (VCC logic and GND) to the Raspberry Pi (usually 5V and GND). **Ensure voltage levels are compatible.**
    * Connect the enable pins (ENA, ENB) of the H-Bridge to Raspberry Pi PWM GPIO pins if you want to control speed (not implemented in this script, but they can be set to HIGH to enable the bridges).

4. **Set the Broker IP Address:**
    * In the Raspberry Pi script (`motor_control.py`) and the computer script (`control_pc.py`), ensure that the variable `broker_ip` matches the IP address of your computer running the Mosquitto Docker container. In the provided scripts, it is set to `192.168.222.119`. **Replace this IP with the correct one for your network.**

5. **Adjust Motor Parameters (Optional):**
    * In the Raspberry Pi script `motor_control.py`, the variable `PASOS_90_GRADOS` is set to `25`. This value depends on the specifications of your stepper motor (how many steps it needs for a full revolution). Adjust this value to achieve the desired movement (e.g., if your motor takes 200 steps per revolution, for 90 degrees it would be 200 / 4 = 50 steps).
    * The `DELAY` variable controls the step speed. Adjust it based on your motor’s capabilities.

## Execution

1. **Run the MQTT Broker:** Ensure the Mosquitto Docker container is running on your computer (`docker-compose up -d`).

2. **Run the Script on the Raspberry Pi:** Connect to your Raspberry Pi via SSH or terminal and run the motor control script:
    ```bash
    python3 motor_control.py
    ```
    You should see the message `📡 Listening for orders on 'ordenes' (YOUR_COMPUTER_IP)...`, indicating the Raspberry Pi is connected to the broker and waiting for commands.

3. **Run the Script on the Computer:** Open a new terminal on your computer and run the control script:
    ```bash
    python3 control_pc.py
    ```
    You should see the message `🔵 Waiting for keys... Press 'i' for left, 'd' for right.`

## Usage

### Once both scripts are running:

* In the computer terminal, press the `'i'` key to send the "left" command to the Raspberry Pi. The motor should rotate 90 degrees counterclockwise (or the direction configured as "left" in the Raspberry Pi script).
* Press the `'d'` key to send the "right" command. The motor should rotate 90 degrees clockwise (or the direction configured as "right").
* Press the `'Esc'` key on the computer to stop the control script.
* To stop the script on the Raspberry Pi, press `Ctrl + C` in its terminal.
