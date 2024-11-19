import cv2
import threading
import socket
from vidgear.gears import VideoGear
from vidgear.gears import NetGear
import pyaudio
import wave

#--------Audio initialize---------------------
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 5
INPUT_INDEX=1                    #run get_input_device_id() and paste in your external camera/headset index
OUTPUT_INDEX=4                   #run get_output_device_id() and paste in your external camera/headset index

p = pyaudio.PyAudio()
stream_sending = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer= CHUNK,input_device_index=INPUT_INDEX)
stream_receive = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer= CHUNK,output_device_index=OUTPUT_INDEX)

#--------Camera initialize---------------------
cam = cv2.VideoCapture(0)
vid_stream = VideoGear(source=1).start()
options = {"flag": 0, "copy": True, "track": False}
server = NetGear(
    address="127.0.0.1",
    port="5454",
    protocol="tcp",
    pattern=1,
    logging=True,
    **options
)
#--------Functions -----------------------------

def set_up_socket(host_ip = socket.gethostbyname(socket.gethostname()), port = 8080):
    '''
	This function set up the socket, connected to host and port which are pasted in as parameter. By default, host would be local host and port would be 8080
	'''
    server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    print('HOST IP:',host_ip)
    socket_address = (host_ip,port)
    server_socket.bind(socket_address)
    server_socket.listen(5)
    print("LISTENING AT:",socket_address)
    return server_socket

def sound_and_camera_send(client_socket:socket.socket, stop_event:threading.Event):
    '''
    This function send a frame from camera and a frame from microphone through the open socket. The microphone could be chosen by the INPUT_INDEX global variable in the Sound initializing part.
    This function can be stopped by the global variable stop_event
    '''
    print('Recording...')
    while True:
        try:
            vid_frame = vid_stream.read()
            sound_frame = stream_sending.read(CHUNK)
            if vid_frame is None:
                break

            server.send(vid_frame) #sending camera frame
            client_socket.send(sound_frame) # sending sound frame

            if stop_event.is_set():
                break

        except KeyboardInterrupt:
            vid_stream.stop()
            server.close()
            stream_sending.close()
            p.terminate()
            break

def sound_receive(client_socket:socket.socket):
    '''
    This function receive a frame of sound from the smartwatch and play it through the selected speaker matching the OUTPUT_INDEX ID in the Sound initializing part
    '''
    while True:
        try:
            frame = client_socket.recv(CHUNK)

            if frame == b'':
                break
            print(frame)
            stream_receive.write(frame)
            if stop_event.is_set():
                break
        except Exception as e:
            print(e)
            break

    stream_receive.close()
    p.terminate()  

def send_a_from_input(client_socket: socket.socket):
    """
    Lee continuamente la entrada del teclado y envía 'a' al socket si se introduce.
    Se detiene cuando el evento stop_event está activado.
    """
    try:
        while not stop_event.is_set():
            user_input = input("Escribe algo y presiona Enter (escribe 'a' para enviar): ").strip()
            if user_input == 'a':
                print("Enviando 'a' al cliente...")
                client_socket.send(b'a')  # Enviar la letra 'a' como bytes
            elif user_input.lower() == 'salir':
                print("Saliendo del envío de datos.")
                stop_event.set()  # Detener el programa
                break
    except Exception as e:
        print(f"Error en send_a_from_input: {e}")
    finally:
        client_socket.close()


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
    # get_input_device_id()
    # get_output_device_id()
    stop_event = threading.Event()
    server_socket = set_up_socket()
    conn, add = server_socket.accept()
    print('Socket connected!')

    send_a_thread = threading.Thread(target=send_a_from_input, args=(conn,), daemon=True)
    send_a_thread.start()

    sound_and_camera_send(conn, stop_event)
    sound_receiving_thread = threading.Thread(target=sound_receive, args=(conn,), daemon=True)
    sound_receiving_thread.start()



