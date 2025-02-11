import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import socket
import struct
import pickle
import threading
import pyaudio
import tkinter as tk
from libraries.tempos import g
from app.niftyclock import NiftyClockScreen
from app.call import IncomingCallScreen
from app.doorbell_screen import DoorbellScreen
import numpy
import cv2
import time

HOST = '192.168.1.147' # '127.0.0.1'
PORT = 5454 #8080

#--------Audio initialize---------------------
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 5
INPUT_INDEX=1                  #run get_input_device_id() and paste in your computer index
OUTPUT_INDEX=3                 #run get_output_device_id() and paste in your computer index

stop_event=threading.Event()

class AppController:
    def __init__(self, g, root):
        self.g = g
        self.root = root
        self.current_screen = None
        self.show_doorbell = False
        self.call_in_progress = False
        self.door_is_open = False
        self.show_nifty_clock_screen()

        self.init_audio()
        self.conn = self.set_up_socket(host=HOST)

        self.client_socket_sound_send = self.conn[0]
        self.client_socket_sound_recv = self.conn[1]
        self.client_socket_video = self.conn[2]
        self.client_socket_ring = self.conn[3]

        self.start_socket_threads()

    def show_nifty_clock_screen(self):
        if self.current_screen:
            self.show_doorbell = False
            self.call_in_progress = False
            self.current_screen.app_end()
        self.current_screen = NiftyClockScreen(self.g, self.root, self)

    def show_incoming_call_screen(self):
        if self.current_screen:
            self.current_screen.app_end()
        self.current_screen = IncomingCallScreen(self.g, self.root, self)

    def show_doorbell_screen(self):
        if self.current_screen:
            self.current_screen.app_end()
        self.current_screen = DoorbellScreen(self.g, self.root, self)
        self.show_doorbell = True

    def open_door(self):
        self.door_is_open = True

    def init_audio(self):
        self.p = pyaudio.PyAudio()
        self.stream_receive = self.p.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer= CHUNK,output_device_index=OUTPUT_INDEX)
        self.stream_sending = self.p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer= CHUNK,input_device_index=INPUT_INDEX)

    def set_up_socket(self, host:str = socket.gethostbyname(socket.gethostname()), ports = [8080, 8081, 8082, 8083]) -> socket.socket:
        '''
        This function set up the socket, connected to host and port which are pasted in as parameter. By default, host would be local host and port would be 8080
        '''
        self.sockets = []

        for port in ports:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print(f'listening at {host}:{port}')
            self.client_socket.connect((host,port)) # a tuple
            self.sockets.append(self.client_socket)

        print('Connected to server')
        return self.sockets
    
    def start_socket_threads(self):       
        """
        This function have 3 threads running, one for sound receiving, one for sound sending and one for video sending, waiting to receive data from the server. All the threads here could be stopped by the stop_event global variable 
        """
        self.sound_thread = threading.Thread(target=self.sound_receive, daemon=True)
        self.video_thread = threading.Thread(target=self.camera_receive, daemon=True)
        self.sound_sending_thread = threading.Thread(target=self.sound_send)
        self.listen_thread = threading.Thread(target=self.listen_for_ring, daemon=True)
        self.send_open_thread = threading.Thread(target=self.send_open, daemon=True)

        self.sound_thread.start()
        self.video_thread.start()
        self.sound_sending_thread.start()
        self.listen_thread.start()
        self.send_open_thread.start()

    def camera_receive(self):
        """
        This function recieve data frame from the server, showing the frame into the cv2 screen every one milisecond
        """
        data = b""
        payload_size = struct.calcsize("Q")
        while True:
            if self.client_socket_video:
                while len(data) < payload_size:
                    packet = self.client_socket_video.recv(4*1024) # 4K
                    if not packet: 
                        break
                    data+=packet

                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack("Q",packed_msg_size)[0]

                while len(data) < msg_size:
                    data += self.client_socket_video.recv(4*1024)

                frame_data = data[:msg_size]
                data  = data[msg_size:]
                frame = pickle.loads(frame_data)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                if stop_event.is_set() or cv2.waitKey(1) == ord('q'):
                    break

                if self.show_doorbell:
                    self.current_screen.draw_frame(frame)
            else:
                pass

    def sound_receive(self):
        '''
        This function receive data sound frame from the server, playing the sound frame through matcheing pre-defined OUTPUT_INDEX device
        '''
        while True:
            try:
                frame = self.client_socket_sound_send.recv(CHUNK)

                if frame == b'':
                    break

                if stop_event.is_set():
                    break

                if self.show_doorbell:
                    self.stream_receive.write(frame)
            except Exception as e:
                print(e)
                break

        self.stream_receive.close()
        self.p.terminate()

    def sound_send(self):
        """
        This function send a frame of sound from the selected microphone by INPUT_INDEX and send it through the socket
        """
        while True:
            try:
                sound_frame = self.stream_sending.read(CHUNK)
                if self.show_doorbell:
                    self.client_socket_sound_recv.send(sound_frame)
                if stop_event.is_set():
                    break
            except Exception as e:
                print(e)
                break

        self.stream_sending.close()
        self.p.terminate()

    def listen_for_ring(self):
        """
        Hear the socket to listen when it hears the word 'ring'.
        If it detects it, change the page to the incoming call, in case it's in the clock.
        """
        try:
            while True:
                data = self.client_socket_ring.recv(1024)  # Read socket

                # Verify if 'ring' is in received data
                if data.strip() == b'ring':
                    if self.call_in_progress == False:
                        print("Ring received: Making the call")
                        self.call_in_progress = True
                        self.show_incoming_call_screen()
                    else:
                        print("Ring received: A call is already in progress")

                if stop_event.is_set():
                    break
        except Exception as e:
            print(f"Error in listen_for_ring: {e}")
        finally:
            self.client_socket.close()

    def send_open(self):
        """
        Wait until the doorbell screen wants to open the door.
        If send_open is true, send 'open' to the doorbell.
        """
        try:
            while True:
                if self.door_is_open == True:
                    print("Sending the open message to the doorbell...")
                    self.client_socket.send(b'open\n')
                    # Send the word 'ring' as bytes
                    self.door_is_open = False
                if stop_event.is_set():
                    break
                time.sleep(1)
        except Exception as e:
            print(f"Error in send_a_from_input: {e}")
        finally:
            self.client_socket.close()

    def start_receiver(self):
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

                if not self.show_doorbell:
                    data = data[msg_size:]
                    continue

                frame_data = data[:msg_size]
                data = data[msg_size:]

                frame = pickle.loads(frame_data)
                if self.show_doorbell:
                    self.current_screen.draw_frame(frame)

if __name__ == "__main__":
    root = tk.Tk()
    g = g(root)
    app = AppController(g, root)
    root.mainloop()
