import cv2
import socket
from vidgear.gears import NetGear
import pyaudio
import threading

#--------Audio initialize---------------------
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 12000
RECORD_SECONDS = 5
INPUT_INDEX=2                  #run get_input_device_id() and paste in your computer index
OUTPUT_INDEX=6                 #run get_output_device_id() and paste in your computer index

p = pyaudio.PyAudio()
stream_recieve = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer= CHUNK,output_device_index=4)
stream_sending = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer= CHUNK,input_device_index=INPUT_INDEX)

#--------Camera initialize---------------------
options = {"flag": 0, "copy": True, "track": False}

client = NetGear(
	address="192.168.56.1",
    port="5454",
    protocol="tcp",
    pattern=1,
    receive_mode=True,
    logging=True,
    **options
	)

#--------Functions------------------------------
stop_event=threading.Event() # global variable to stop the functions

def set_up_socket(host:str= socket.gethostbyname(socket.gethostname()), port:int = 8080) -> socket.socket:
	'''
	This function set up the socket, connected to host and port which are pasted in as parameter. By default, host would be local host and port would be 8080
	'''
	client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	print(f'listening at {host}:{port}')
	client_socket.connect((host,port)) # a tuple
	print('Connected to server', host, '+ ', port)
	return client_socket

def camera_recieve():
	"""
	This function recieve data frame from the server, showing the frame into the cv2 screen every one milisecond
	"""
	while True:
		vid_frame = client.recv()
		if vid_frame is None:
			break
		cv2.imshow("Smartwatch Frame", vid_frame)
		key = cv2.waitKey(1) & 0xFF
		if key == ord("q") or stop_event.is_set():
			break
	cv2.destroyAllWindows()
	client.close()

def sound_recieve(client_socket:socket.socket):
	'''
	This function recieve data sound frame from the server, playing the sound frame through matcheing pre-defined OUTPUT_INDEX device
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

def sound_send(client_socket:socket.socket):
	"""
	This function send a frame of sound from the selected microphone by INPUT_INDEX and send it through the socket
	"""
	while True:
		try:
			sound_frame = stream_sending.read(CHUNK)
			client_socket.send(sound_frame)
			if stop_event.is_set():
				break
		except Exception as e:
			print(e)
			break

	stream_sending.close()
	p.terminate()

def sound_and_video_recieve(client_socket:socket.socket):
	"""
	This function have 2 threads running, one for sound and one for video, waiting to recieve data from the server. All the threads here could be stopped by the stop_event global variable 
	"""
	sound_thread = threading.Thread(target=sound_recieve, args=(client_socket,), daemon=True)
	sound_thread.start()
	video_thread = threading.Thread(target=camera_recieve, daemon=True)
	video_thread.start()

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
	this functions return back all the available output device by ID and name -> update the wanted device id OUTPUT_INDEX global variable in the Sound initializing part 
	"""
	p = pyaudio.PyAudio()
	info = p.get_host_api_info_by_index(0)
	numdevices = info.get('deviceCount')
	for i in range(0, numdevices):
		if (p.get_device_info_by_index(i).get('maxOutputChannels')) > 0:
			print("Output Device id ", i, " - ", p.get_device_info_by_index(i).get('name'))
	p.terminate()

if __name__ == "__main__":
	client_socket = set_up_socket()
	sound_and_video_recieve(client_socket)

	sound_sending_thread = threading.Thread(target=sound_send, args=(client_socket,))
	sound_sending_thread.start()

	input = input('Stop? (y/n)')
	if input == 'y':
		stop_event.set()

