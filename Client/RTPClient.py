import socket
import pyaudio
import tkinter as tk
from tkinter import filedialog
import threading

class RTPClient:
    def __init__(self, root):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = ('localhost', 5004)
        self.chunk_size = 1024
        self.p = pyaudio.PyAudio()
        self.is_streaming = False
        self.sequence_number = 0
        self.total_chunks = 112  # Exemplo, ajuste conforme necessário

        # Configura PyAudio
        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=44100,
                                  input=True,
                                  frames_per_buffer=self.chunk_size)

        # Configuração da interface gráfica
        self.root = root
        self.root.title("RTP Client")

        self.start_button = tk.Button(self.root, text="Iniciar Streaming de Áudio", command=self.start_streaming)
        self.start_button.pack(pady=20)

        self.stop_button = tk.Button(self.root, text="Parar Streaming de Áudio", command=self.stop_streaming)
        self.stop_button.pack(pady=20)

    def start_streaming(self):
        if not self.is_streaming:
            self.is_streaming = True
            self.stream_thread = threading.Thread(target=self.stream_audio)
            self.stream_thread.start()

    def stop_streaming(self):
        self.is_streaming = False
        self.stream_thread.join()  # Espera o thread terminar
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

    def stream_audio(self):
        try:
            while self.is_streaming:
                audio_data = self.stream.read(self.chunk_size)
                self.send_message(audio_data)
        except Exception as e:
            print(f"Erro ao transmitir áudio: {e}")

    def send_message(self, data):
        try:
            # Enviar mensagem de áudio com cabeçalho
            header = f'audio|{self.sequence_number}|{self.total_chunks}|RIFF$'.encode()
            message = header + b'|' + data
            self.socket.sendto(message, self.server_address)
            self.sequence_number += 1  # Incrementa o número de sequência
        except Exception as e:
            print(f"Erro ao enviar mensagem: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    client = RTPClient(root)
    root.mainloop()
