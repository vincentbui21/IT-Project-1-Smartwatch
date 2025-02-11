import cv2
import threading
import socket
import pyaudio
import pickle
import struct
import imutils
import time

#--------Audio initialize---------------------
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
INPUT_INDEX=1                    #run get_input_device_id() and paste in your external camera/headset index
OUTPUT_INDEX=3                   #run get_output_device_id() and paste in your external camera/headset index

p = pyaudio.PyAudio()
stream_sending = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer= CHUNK,input_device_index=INPUT_INDEX)
stream_recieve = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer= CHUNK,output_device_index=OUTPUT_INDEX)

#--------Camera initialize---------------------

#--------Functions -----------------------------

def set_up_socket(host_ip = socket.gethostbyname(socket.gethostname()), ports = [8080,8081,8082,8083]):
    '''
	This function set up the socket, connected to host and port which are pasted in as parameter. By default, host would be local host and port would be 8080
	'''
    conns = []

    print("LISTENING AT:" + host_ip)
    for port in ports:
        client_socket= socket.socket(socket.AF_INET,socket.SOCK_STREAM)

        client_socket.bind((host_ip,port))
        client_socket.listen(1)
        conn , addr = client_socket.accept()
        print('...')
        conns.append(conn)

    return conns

def video_send(client_socket_video:socket.socket):
    vid = cv2.VideoCapture(0)
    
    while True:
        img, frame = vid.read()
        a = pickle.dumps(frame)
        msg = struct.pack('Q', len(a))+a
        client_socket_video.sendall(msg)

        if stop_event.is_set() or cv2.waitKey(1) == ord('q'):
            break

def sound_send(client_socket_sound:socket.socket):
    while True:
        try:
            sound_frame = stream_sending.read(CHUNK)
            client_socket_sound.send(sound_frame) # sending sound frame

            if stop_event.is_set():
                break

        except KeyboardInterrupt:
            stream_sending.close()
            p.terminate()
            break

def sound_recieve(client_socket:socket.socket):
    '''
    This function recieve a frame of sound from the smartwatch and play it through the selected speaker matching the OUTPUT_INDEX ID in the Sound initializing part
    '''
    while True:
        try:
            frame = client_socket.recv(CHUNK)

            if frame == b'':
                break
            stream_recieve.write(frame)
            if stop_event.is_set():
                break
        except Exception as e:
            print(e)
            break

    stream_recieve.close()
    p.terminate()  

def send_ring_from_input(client_socket: socket.socket):
    """
    Read the keyboard and send 'ring' to the socket if enter is clicked.
    Stop when stop_event is set.
    """
    try:
        while not stop_event.is_set():
            user_input = input("Press 'enter' to ring the bell. Write 'exit' to end: ").strip()
            if user_input == '':
                print("Sending the message to the smartwatch...")
                client_socket.send(b'ring\n')  # Send the word 'ring' as bytes
            elif user_input.lower() == 'exit':
                print("Exiting data sending.")
                stop_event.set()  # Stop the program
                break
    except Exception as e:
        print(f"Error in send_a_from_input: {e}")
    finally:
        client_socket.close()

def open_door(client_socket: socket.socket):
    """
    This function listen to command from the smartwatch whether to open the door or not. It utilize the send_ring_from_input socket
    """
    while True:
        data = client_socket.recv(1024)
        if data.strip() == b'open':
            print('\nDoor opened, you can enter the house!')

        if stop_event.is_set():
            break

def get_input_device_id():
    """
	this functions return back all the available input device by ID and name -> update the wanted device id in INPUT_INDEX global variable in the Sound initializing part 
	"""
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')

    for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))

def get_output_device_id():
    """
	this functions return back all the available output device by ID and name -> update the wanted device id in OUTPUT_INDEX global variable in the Sound initializing part 
	"""
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    for i in range(0, numdevices):
        if (p.get_device_info_by_index(i).get('maxOutputChannels')) > 0:
            print("Output Device id ", i, " - ", p.get_device_info_by_index(i).get('name'))
    p.terminate()

if __name__ == "__main__":
    stop_event = threading.Event()
    conn = set_up_socket(host_ip="192.168.1.147")
    conn_sound_send = conn[0] #port 8080
    conn_sound_recv = conn[1] #port 8081
    conn_video = conn[2] #port 8082
    conn_ring = conn[3] #port 8083

    print('Socket connected!')

    sound_sending_thread = threading.Thread(target=sound_send, args=(conn_sound_send,), daemon=True)
    sound_receiving_thread = threading.Thread(target=sound_recieve, args=(conn_sound_recv,), daemon=True)
    video_sending_thread = threading.Thread(target=video_send, args=(conn_video,), daemon=True)
    send_a_thread = threading.Thread(target=send_ring_from_input, args=(conn_ring,), daemon=True)
    open_door_thread = threading.Thread(target=open_door, args=(conn_ring,), daemon= True)
    
    send_a_thread.start()
    sound_receiving_thread.start()
    sound_sending_thread.start()
    video_sending_thread.start()
    open_door_thread.start()

    while True:
        if stop_event.is_set():
            break


