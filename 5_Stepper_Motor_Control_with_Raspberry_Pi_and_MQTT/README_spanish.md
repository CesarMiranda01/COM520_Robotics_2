# Stepper Motor Control with Raspberry Pi and MQTT

![Stepper Motor Control](https://via.placeholder.com/800x400?text=Stepper+Motor+Control+System)

This project demonstrates how to control a bipolar stepper motor using a Raspberry Pi, an L298N H-Bridge, and MQTT communication. The Raspberry Pi subscribes to an MQTT broker (running in a Docker container) to receive commands from a computer and actuate the motor accordingly.

## 🎯 Project Overview

A wireless control system that allows remote operation of a stepper motor through keyboard commands, using MQTT protocol for communication between a computer and Raspberry Pi.

## 📋 Components

### Hardware:
* **Raspberry Pi:** The system's brain, responsible for executing Python code to control the motor and communicate with the MQTT broker.
* **L298N H-Bridge:** Power interface between the Raspberry Pi and the stepper motor, allowing control of direction and current flow to the motor coils.
* **Bipolar Stepper Motor:** The device that will move according to received commands.
* **Computer:** Used to send control commands to the motor through the MQTT broker.
* **Jumper Wires:** For interconnecting components.

### Software:
* **MQTT Broker (Mosquitto in Docker):** A messaging server that facilitates communication between the computer and Raspberry Pi.

## 🔗 System Architecture
