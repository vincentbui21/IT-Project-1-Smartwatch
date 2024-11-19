import socket
import wave
import time
import subprocess
import os

# Paramètres de connexion
HOST = '127.0.0.1'  # Adresse IP de la montre (ajustez selon votre configuration)
PORT = 12345        # Port à utiliser

# Chemin du fichier audio
AUDIO_FILE = "src/apps/tests/output.wav"
CONVERTED_FILE = "src/apps/tests/outside-8kHz-mono.wav"  # Fichier de sortie en cas de conversion

def check_and_convert_audio(file_path):
    print("Vérification du fichier audio...")
    try:
        with wave.open(file_path, 'rb') as wf:
            framerate = wf.getframerate()
            channels = wf.getnchannels()
            print(f"Taux d'échantillonnage : {framerate} Hz, Canaux : {channels}")

            # Vérifier si le fichier est en 8 kHz et mono
            if framerate == 8000 and channels == 1:
                print("Le fichier audio est déjà en 8 kHz et mono.")
                return file_path  # Retourne le chemin du fichier original

            else:
                print("Le fichier audio doit être converti en 8 kHz et mono.")
                # Conversion avec FFmpeg
                subprocess.run([
                    'ffmpeg', '-i', file_path,
                    '-ar', '8000',         # Fréquence d'échantillonnage à 8 kHz
                    '-ac', '1',            # Mono
                    '-sample_fmt', 's16',  # Format PCM 16 bits
                    CONVERTED_FILE
                ], check=True)
                print("Conversion terminée. Utilisation du fichier converti.")
                return CONVERTED_FILE  # Retourne le chemin du fichier converti

    except wave.Error:
        print("Erreur : le fichier audio n'est pas au format WAV.")
        return None

def send_audio():
    print("Démarrage de la transmission audio...")
    # Vérifier et convertir le fichier si nécessaire
    audio_file = check_and_convert_audio(AUDIO_FILE)
    if audio_file is None:
        print("Le fichier audio n'est pas valide. Arrêt du programme.")
        return

    # Charger le fichier audio converti ou original
    try:
        with wave.open(audio_file, 'rb') as wf:
            # Configuration du socket
            print("Connexion au récepteur...")
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.connect((HOST, PORT))
                    print("Connecté au récepteur audio.")

                    # Lire et envoyer les échantillons audio
                    data = wf.readframes(1024)
                    while data:
                        s.sendall(data)
                        print("Paquet envoyé")
                        time.sleep(0.125)  # Ajuster selon les performances de réception
                        data = wf.readframes(1024)

                    print("Transmission audio terminée.")

                except socket.error as e:
                    print(f"Erreur de connexion : {e}")
    except FileNotFoundError:
        print("Erreur : le fichier audio n'existe pas.")
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")

    # Message de fin de transmission
    print(f"Fichier '{audio_file}' transmis avec succès.")

# Lancer l'envoi de l'audio
send_audio()