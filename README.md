# Smart Doorbell with Smartwatch Integration

🔹 **A smart doorbell system that integrates with a smartwatch, allowing users to see visitors, communicate, and remotely unlock the door.**

## 📌 Overview
This project features a **smart doorbell** equipped with a **camera** that sends notifications to a **smartwatch** via **WiFi** when a visitor rings the bell. The user can **answer the call, see the visitor, communicate**, and even **unlock the door remotely** if they trust the visitor, without being physically at the door.

---

## 🏠 **Part 1: Doorbell System**
The **doorbell** is responsible for handling visitor detection and communication.

### 🔧 Features
- Uses **Python** for implementation.
- Connects to the network via **WiFi**.
- Opens a **TCP port** for communication with the smartwatch.
- Captures and streams video from the **camera**.
- Sends **incoming call notifications** to the smartwatch.

### 🛠️ Technologies Used
- **Python**
- **OpenCV** (for camera functionality)
- **Socket Programming** (for TCP communication)

---

## ⌚ **Part 2: Smartwatch Application**
The **smartwatch application** provides the user interface for interacting with the smart doorbell.

### 📱 Features
- Built using **Tkinter** for GUI design.
- Maintains three different UI states:
  1. **Idle UI** – Displays **time and date** when no activity is detected.
  2. **Incoming Call UI** – Displays an alert when the doorbell rings, with **Accept** and **Decline** buttons.
  3. **Active Call UI** – Streams the **live video feed** from the doorbell camera when the call is accepted.<br>
  ![Screenshot 2025-02-11 210051](https://github.com/user-attachments/assets/abd22c04-c78f-4b52-a961-ec3a0b646ce8)

- Allows users to **communicate with visitors** and **unlock the door remotely**.

### 🛠️ Technologies Used
- **Python**
- **Tkinter** (for UI development)
- **Socket Programming** (for TCP communication)

---

## 🚀 Installation & Setup
### **Prerequisites**
- A **Raspberry Pi** or similar device for the doorbell system.
- A **camera module** for capturing video.
- A **smartwatch** running a **Tkinter-based Python application**.
- A **WiFi network** for communication.

### **Setting Up the Doorbell**
1. Install dependencies:
   ```bash
   pip install opencv-python numpy socket pyaudio tkinter
   ```
2. Ensure the following Python modules are imported:
   ```python
   import socket
   import struct
   import pickle
   import threading
   import pyaudio
   import tkinter as tk
   import numpy
   import cv2
   import time
   ```
3. Run the doorbell script:
   ```bash
   python doorbell.py
   ```

### **Setting Up the Smartwatch Application**
1. Install dependencies:
   ```bash
   pip install opencv-python numpy socket pyaudio tkinter
   ```
2. Run the smartwatch UI application:
   ```bash
   python smartwatch.py
   ```

### **Setting Up TCP Port Forwarding with ngrok**
If the smartwatch and doorbell are on different networks, you can use **ngrok** to expose the TCP port over the internet.

1. **Download and install ngrok** from [ngrok's official website](https://ngrok.com/).
2. **Authenticate ngrok** (only required once):
   ```bash
   ngrok config add-authtoken YOUR_AUTH_TOKEN
   ```
3. **Start a TCP tunnel** on the port used by the doorbell:
   ```bash
   ngrok tcp <YOUR_DOORBELL_PORT>
   ```
4. **Get the generated public address** (e.g., `tcp://x.tcp.ngrok.io:12345`).
5. **Modify the smartwatch application** to connect to this address instead of a local network address.

---

## 🎮 How It Works
1. **A visitor rings the smart doorbell.**
2. **The doorbell sends a notification** to the smartwatch via WiFi.
3. **The smartwatch displays an incoming call UI**, allowing the user to accept or decline.
4. If accepted, **the video stream starts** and the user can communicate with the visitor.
5. The user can **choose to unlock the door remotely** if they trust the visitor. <br>

![Screenshot 2025-02-11 210110](https://github.com/user-attachments/assets/238e62f6-0a11-4e42-9610-f8e2bdcb06ff)

---

## 📜 License
This project is open-source under the **MIT License**. Contributions are welcome!

## 🙌 Credits
Developed by **Vincent Bui** and team.
