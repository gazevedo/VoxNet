import tkinter as tk
from tkinter import scrolledtext, filedialog
import socket
import threading
import pyaudio

from Client.VoiPClient import VoiPClient

voipClinet = VoiPClient()

class ClientUi:
    def __init__(self, master):
        self.master = master
        self.top = tk.Toplevel(master)
        self.top.title("VoIP Client Interface")

        self.create_widgets()

        # Inicialize o socket para o streaming de áudio
        self.audio_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.audio_stream_thread = None

    def create_widgets(self):
        tk.Label(self.top, text="Enviar SIP").grid(row=0, column=0, padx=10, pady=5)
        self.sip_entry = tk.Entry(self.top, width=50)
        self.sip_entry.grid(row=0, column=1, padx=10, pady=5)
        self.sip_send_button = tk.Button(self.top, text="Enviar SIP", command=self.send_sip)
        self.sip_send_button.grid(row=0, column=2, padx=10, pady=5)

        tk.Label(self.top, text="Enviar RTP").grid(row=1, column=0, padx=10, pady=5)
        self.rtp_entry = tk.Entry(self.top, width=50)
        self.rtp_entry.grid(row=1, column=1, padx=10, pady=5)
        self.rtp_send_button = tk.Button(self.top, text="Enviar RTP", command=self.send_rtp)
        self.rtp_send_button.grid(row=1, column=2, padx=10, pady=5)

        tk.Label(self.top, text="Enviar RTCP").grid(row=2, column=0, padx=10, pady=5)
        self.rtcp_entry = tk.Entry(self.top, width=50)
        self.rtcp_entry.grid(row=2, column=1, padx=10, pady=5)
        self.rtcp_send_button = tk.Button(self.top, text="Enviar RTCP", command=self.send_rtcp)
        self.rtcp_send_button.grid(row=2, column=2, padx=10, pady=5)

        tk.Label(self.top, text="Enviar Áudio").grid(row=3, column=0, padx=10, pady=5)
        self.audio_button = tk.Button(self.top, text="Selecionar e Enviar Áudio", command=self.send_audio)
        self.audio_button.grid(row=3, column=1, padx=10, pady=5)

        # Novo botão para iniciar streaming de áudio
        self.start_stream_button = tk.Button(self.top, text="Iniciar Streaming de Áudio", command=self.start_audio_streaming)
        self.start_stream_button.grid(row=4, column=1, padx=10, pady=5)

        self.client_log_area = scrolledtext.ScrolledText(self.top, width=80, height=10, state='disabled')
        self.client_log_area.grid(row=5, column=0, columnspan=3, padx=10, pady=10)

    def log(self, message):
        self.client_log_area.config(state='normal')
        self.client_log_area.insert(tk.END, message + '\n')
        self.client_log_area.config(state='disabled')
        self.client_log_area.yview(tk.END)

    def send_sip(self):
        message = self.sip_entry.get()
        result = voipClinet.send_message(message, ('localhost', 5060), 'text', 0, 1)
        self.log(result)

    def send_rtp(self):
        message = self.rtp_entry.get()
        result = voipClinet.send_message(message, ('localhost', 5004), 'text', 0, 1)
        self.log(result)

    def send_rtcp(self):
        message = self.rtcp_entry.get()
        result = voipClinet.send_message(message, ('localhost', 5005), 'text', 0, 1)
        self.log(result)

    def send_audio(self):
        file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav")])
        if file_path:
            try:
                chunk_size = 1024
                with open(file_path, 'rb') as f:
                    # Calcular o tamanho total e o número de pacotes
                    f.seek(0, 2)  # Mover para o final do arquivo
                    total_size = f.tell()
                    f.seek(0)  # Retornar ao início
                    total_chunks = (total_size // chunk_size) + (1 if total_size % chunk_size > 0 else 0)

                    seq = 0
                    audio_data = f.read(chunk_size)
                    while audio_data:
                        message = audio_data
                        self.send_message(message, ('localhost', 5004), 'audio', seq, total_chunks)
                        seq += 1
                        audio_data = f.read(chunk_size)

            except Exception as e:
                self.log(f"Erro ao enviar áudio: {e}")

    def start_audio_streaming(self):
        """Inicia o streaming de áudio."""
        self.audio_stream_thread = threading.Thread(target=self.stream_audio)
        self.audio_stream_thread.start()

    def stream_audio(self):
        chunk_size = 1024
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=44100,
                        input=True,
                        frames_per_buffer=chunk_size)

        try:
            seq = 0
            while True:
                audio_data = stream.read(chunk_size, exception_on_overflow=False)
                self.send_message(audio_data, ('localhost', 5004), message_type='audio', seq=seq, queue_length=0)
                seq += 1
        except Exception as e:
            self.log(f"Erro ao transmitir áudio: {e}")
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()

    def send_message(self, message, address, message_type, seq, queue_length):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            # Converte a mensagem para bytes se for uma string
            if isinstance(message, str):
                message = message.encode()

            # Calcula o tamanho do pacote
            package_size = len(message)

            # Formata a mensagem conforme o protocolo especificado
            if message_type in ['text', 'audio', 'rtcp']:
                formatted_message = f'{message_type}|{seq}|{queue_length}|{package_size}|'.encode() + message
            else:
                raise ValueError("Tipo de mensagem não suportado")

            # Envia a mensagem para o endereço especificado
            sock.sendto(formatted_message, address)
            self.log(f"Enviado para {address}: {formatted_message[:50]}...")  # Log mostrando parte da mensagem

        except Exception as e:
            self.log(f"Erro ao enviar mensagem: {e}")
        finally:
            sock.close()  # Certifique-se de fechar o socket


