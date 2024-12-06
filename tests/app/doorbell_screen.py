import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import cv2
import socket
import struct
import pickle
from time import sleep
from PIL import Image, ImageTk
from libraries.micropython import const
from libraries.tempos import g, rtc, sched
from libraries.graphics import LIGHTGREEN, RED, WHITE, BLACK
from libraries.fonts import roboto8, roboto10
import tkinter as tk
from datetime import datetime

DISPLAY_WIDTH = 210
DISPLAY_HEIGHT = 150

BUTTON_WIDTH = 80
BUTTON_HEIGHT = 27
BUTTON_Y = 199
HANG_UP_X = 30
OPEN_X = 135
RADIUS = 8

HOST = '127.0.0.1' #'192.168.1.117'
PORT = 65432 #8080

class DoorbellScreen:
    def __init__(self, g, root, controller):
        self.g = g
        self.root = root
        self.controller = controller
        self.minute = -1
        self.day = -1
        self.g.canvas.bind("<Button-1>", self.on_click)
        self.root.bind("<Key-space>", self.on_key_pressed)
        self.app_init()

    # Function to display the time and date
    def display_time_and_date(self):
        # Take and format data
        now = datetime.now()
        if self.minute != now.minute:
            self.minute = now.minute
            time_str = now.strftime("%H:%M")
            
            # Clear up screen
            self.g.fill_rect(0, 0, 120, 30, BLACK)
            
            # Display time on the top left
            self.g.setfont(roboto10)
            self.g.setfontalign(-1, -1)
            self.g.text(time_str, 10, 10, WHITE)

            if self.day != now.day:
                self.day = now.day
                self.display_date(now)

            # Show the screen
            self.g.show()

    def display_date(self, now):
        # Clear up screen
        self.g.fill_rect(120, 0, 120, 30, BLACK)
        date_str = now.strftime("%d %b %Y")

        # Display date on the top right
        self.g.setfontalign(1, -1)
        self.g.text(date_str, 230, 10, WHITE)

    def draw_frame(self, frame_data):
        frame_data = cv2.resize(frame_data, (DISPLAY_WIDTH, DISPLAY_HEIGHT))
        frame = Image.fromarray(frame_data)
        tk_img = ImageTk.PhotoImage(frame)
        
        global last_image
        last_image = tk_img

        self.g.canvas.create_image(15, 34, anchor='nw', image=tk_img)
        self.g.show()

    # Function to display the interface with image and buttons
    def display_interface(self):
        self.g.setfontalign(0, 0)
        # Buttons
        self.g.setfont(roboto8)
        
        self.g.fill_rounded_rect(HANG_UP_X, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, RADIUS, RED)  # Red button for "Hang up"
        self.g.text("Hang up", 70, 212, WHITE)
        
        self.g.fill_rounded_rect(OPEN_X, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, RADIUS, LIGHTGREEN)  # Green button for "Open"
        self.g.text("Open", 175, 212, WHITE)

    def start_receiver(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            print("Connected to server.")
            data = b""
            payload_size = struct.calcsize("Q")

            while not self.ticker_flag.is_set():
                while len(data) < payload_size:
                    packet = s.recv(4096)
                    if not packet:
                        print("Connection closed by server.")
                        return
                    data += packet
                
                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack("Q", packed_msg_size)[0]

                while len(data) < msg_size:
                    data += s.recv(4096)

                frame_data = data[:msg_size]
                data = data[msg_size:]

                frame = pickle.loads(frame_data)
                self.draw_frame(frame)

    def on_click(self, event):
        # Check if click is within the Decline or Accept button area
        if HANG_UP_X <= event.x <= HANG_UP_X + BUTTON_WIDTH and BUTTON_Y <= event.y <= BUTTON_Y + BUTTON_HEIGHT:
            self.controller.show_nifty_clock_screen()

        if OPEN_X <= event.x <= OPEN_X + BUTTON_WIDTH and BUTTON_Y <= event.y <= BUTTON_Y + BUTTON_HEIGHT:
            self.controller.open_door()

    def on_key_pressed(self, event):
        # Change the page to the Call screen
        self.controller.show_nifty_clock_screen()

    def app_init(self):
        self.g.fill(BLACK)
        self.display_interface()
        self.display_time_and_date()
        self.ticker_flag, self.ticker_thread = sched.setInterval(100, self.display_time_and_date)
        # self.start_receiver()

    def app_end(self):
        if self.ticker_thread:
            sched.clearInterval(self.ticker_flag, self.ticker_thread)
        sleep(0.2)
        self.g.fill(BLACK)

if __name__ == "__main__":
    root = tk.Tk()
    g = g(root)
    DoorbellScreen(g, root, None)  # Create and display the incoming call screen
    root.mainloop()