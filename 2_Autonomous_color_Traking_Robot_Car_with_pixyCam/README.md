# Autonomous Color-Tracking Robot Car

![Robot Car Demo](img_gif.gif)
*Real-time color tracking and autonomous movement*

## 📋 Project Overview

This project implements an autonomous robot car that uses computer vision to detect and track colored objects. The system combines a Pixy2 camera with motor control algorithms to enable real-time object tracking and pursuit.

## 🛠️ Hardware Components

### Robot Chassis Kit
- **2x** DC geared motors with encoders
- **2x** Rubber wheels (6.5 x 2.7 cm)
- **1x** Caster wheel
- **1x** Battery holder for 2x AA batteries
- **4x** Motor mounts
- M3 screws and nuts
- **4x** M3 spacers
- Acrylic chassis (approx. 20 x 14 cm)
- 2x AA batteries

### Electronic Modules
- **Arduino UNO R3** (ATMEGA 328P) with USB cable
- **L298N Dual Motor Controller** (H-Bridge)
- **Pixy2 Smart Vision Sensor** - Color recognition camera compatible with Arduino, Raspberry Pi, and BeagleBone Black

### Additional Components
- Push-button switch (10x15 mm, 2 pins, 250V, On/Off)
- Jumper wires (10 cm, M-M / M-F / F-F)

## 🚀 Features

- **Real-time color detection** using Pixy2 camera
- **Smooth object tracking** with adaptive motor control
- **Proportional control system** for precise movement
- **Serial monitoring** of tracking data and motor outputs
- **Configurable parameters** for different tracking scenarios

## 📁 Code Structure

### Main Files:
- `cocheCamera.ino` - Main control logic for object tracking and motor control
- `Tracker.h/cpp` - Pixy2 camera interface and object tracking functions
- `Rueda.h/cpp` - Motor control library for wheel movement

### Key Functions:
- `calculatePower()` - Computes motor power based on object position
- `getSmoothedX()` - Provides filtered object coordinates
- `mover()` - Controls individual wheel movement

## ⚙️ Installation & Setup

1. **Hardware Assembly:**
   - Mount motors and wheels on chassis
   - Install Pixy2 camera at the front
   - Connect L298N motor driver to Arduino
   - Wire power switch and battery holder

2. **Software Setup:**
   ```bash
   # Install required libraries
   Arduino IDE → Sketch → Include Library → Manage Libraries
   - Install "Pixy2" library
   - Install "Servo" library (if needed)

## License

This project is part of Robotics 2 coursework. Feel free to use and modify for educational purposes. Consulting to owner (me).