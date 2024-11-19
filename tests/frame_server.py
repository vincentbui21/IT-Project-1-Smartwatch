import socket
import cv2
import pickle
import struct
import time

def send_video_frames(video_path):
    # Server address setup
    HOST = '127.0.0.1' #'192.168.1.117'  # Change this to match the receiver's IP address
    PORT = 65432 #8080
    socket_address = (HOST, PORT)

    # Socket creation and connection
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(socket_address)
    server_socket.listen(5)
    print(f"Server listening at: {socket_address}")

    # Wait for a client to connect
    client_socket, addr = server_socket.accept()
    print(f"Connection from: {addr}")

    # Capture video
    video = cv2.VideoCapture(video_path)

    try:
        while True:
            ret, frame = video.read()
            if not ret:
                print("No more frames to send.")
                break

            # Convert the frame to RGB and serialize it
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            data = pickle.dumps(frame)

            # Pack message with size info and send
            message = struct.pack("Q", len(data)) + data
            client_socket.sendall(message)
            print(f"Sent frame of size: {len(data)}")

            time.sleep(0.03)  # Control frame rate

    except Exception as e:
        print(f"Error while sending frames: {e}")

    finally:
        video.release()
        server_socket.close()
        print("Connection closed.")

# Call the function with the path to your video file
send_video_frames('src/apps/tests/video.mp4')
