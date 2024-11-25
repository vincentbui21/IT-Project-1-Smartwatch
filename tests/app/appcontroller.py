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
from vidgear.gears import NetGear

HOST = '127.0.0.1' #'10.214.4.53'
PORT = 5454 #8080

#--------Audio initialize---------------------
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 5
INPUT_INDEX=1                  #run get_input_device_id() and paste in your computer index
OUTPUT_INDEX=4                 #run get_output_device_id() and paste in your computer index

#--------Camera initialize---------------------
options = {"flag": 0, "copy": True, "track": False}

client = NetGear(
	address="127.0.0.1",
    port="5454",
    protocol="tcp",
    pattern=1,
    receive_mode=True,
    logging=True,
    **options
)

stop_event=threading.Event()

class AppController:
    def __init__(self, g, root):
        self.g = g
        self.root = root
        self.current_screen = None
        self.show_doorbell = False
        self.call_in_progress = False
        self.show_nifty_clock_screen()

        self.init_audio()
        self.client_socket = self.set_up_socket()
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

    def init_audio(self):
        self.p = pyaudio.PyAudio()
        self.stream_receive = self.p.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer= CHUNK,output_device_index=OUTPUT_INDEX)
        self.stream_sending = self.p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer= CHUNK,input_device_index=INPUT_INDEX)

    def set_up_socket(self, host:str = socket.gethostbyname(socket.gethostname()), port:int = 8080) -> socket.socket:
        '''
        This function set up the socket, connected to host and port which are pasted in as parameter. By default, host would be local host and port would be 8080
        '''
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f'listening at {host}:{port}')
        self.client_socket.connect((host,port)) # a tuple
        print('Connected to server', host, '+ ', port)
        return self.client_socket
    
    def start_socket_threads(self):       
        """
        This function have 3 threads running, one for sound receiving, one for sound sending and one for video sending, waiting to receive data from the server. All the threads here could be stopped by the stop_event global variable 
        """
        self.sound_thread = threading.Thread(target=self.sound_receive, daemon=True)
        self.sound_thread.start()

        self.video_thread = threading.Thread(target=self.camera_receive, daemon=True)
        self.video_thread.start()

        self.sound_sending_thread = threading.Thread(target=self.sound_send)
        self.sound_sending_thread.start()

        self.listen_thread = threading.Thread(target=self.listen_for_ring, daemon=True)
        self.listen_thread.start()

    def camera_receive(self):
        """
        This function receive data frame from the server, showing the frame into the cv2 screen every one milisecond
        """
        while True:
            vid_frame = client.recv()
            if vid_frame is None:
                break

            if stop_event.is_set():
                break

            if self.show_doorbell:
                self.current_screen.draw_frame(vid_frame)
            
        client.close()

    def sound_receive(self):
        '''
        This function receive data sound frame from the server, playing the sound frame through matcheing pre-defined OUTPUT_INDEX device
        '''
        while True:
            try:
                frame = self.client_socket.recv(CHUNK)

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
                    self.client_socket.send(sound_frame)
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
            buffer = b''
            while True:
                data = self.client_socket.recv(1024)
                buffer += data  # Save all the data
                if b'ring' in buffer:
                    buffer = b''  # Reset the buffer after reading
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
