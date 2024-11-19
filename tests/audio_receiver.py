import socket
import pyaudio
import tkinter as tk

# Initialisation de PyAudio pour la sortie audio
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt8, channels=1, rate=8000, output=True)

# Interface utilisateur simulée pour la smartwatch
root = tk.Tk()
root.title("Simulateur de Smartwatch - Réception Audio")

status_label = tk.Label(root, text="En attente de connexion...", font=("Helvetica", 14))
status_label.pack(pady=20)

def receive_audio():
    HOST = ''
    PORT = 12345

    # Configuration du socket pour la réception d'audio
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        status_label.config(text="En attente de connexion...")
        root.update()

        conn, addr = s.accept()
        status_label.config(text=f"Connecté à {addr}")
        root.update()

        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                stream.write(data)
        except KeyboardInterrupt:
            status_label.config(text="Réception interrompue.")
        finally:
            conn.close()
            stream.stop_stream()
            stream.close()
            p.terminate()
            s.close()
            status_label.config(text="Connexion fermée.")
            root.update()

# Démarrer la réception d'audio
root.after(100, receive_audio)
root.mainloop()