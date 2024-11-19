import tkinter as tk
import pickle
import socket
import cv2
import struct
from PIL import Image, ImageTk
from libraries.graphics import MockGraphics

DISPLAY_WIDTH = 240
DISPLAY_HEIGHT = 240

root = tk.Tk()
g = MockGraphics(root)

def draw_frame(frame_data):
    frame_data = cv2.resize(frame_data, (DISPLAY_WIDTH, DISPLAY_HEIGHT))
    frame = Image.fromarray(frame_data)
    tk_img = ImageTk.PhotoImage(frame)
    
    global last_image
    last_image = tk_img

    g.canvas.create_image(0, 0, anchor='nw', image=tk_img)
    g.show()
    root.update()

def start_receiver():
    HOST = '127.0.0.1' #'192.168.1.117'
    PORT = 65432 #8080

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print("Connected to server.")
        data = b""
        payload_size = struct.calcsize("Q")

        while True:
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
            draw_frame(frame)

start_receiver()
root.mainloop()
