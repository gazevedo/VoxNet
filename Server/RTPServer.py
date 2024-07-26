import socket
import pyaudio
import threading
import time  # Adicione esta linha para importar o módulo time


class RTPServer:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('localhost', 5004))
        self.chunk_size = 1024
        self.audio_buffer = []
        self.total_chunks = None
        self.lock = threading.Lock()
        print("RTP Server iniciado.")

        # Configura PyAudio
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=44100,
                                  output=True)
        self.is_running = True
        self.buffer_thread = threading.Thread(target=self.play_audio_buffer)
        self.buffer_thread.start()

    def start(self):
        while self.is_running:
            data, addr = self.socket.recvfrom(65535)  # Aumente o tamanho do buffer
            self.handle_data(data, addr)

    def handle_data(self, data, addr):
        try:
            first_pipe = data.find(b'|')
            second_pipe = data.find(b'|', first_pipe + 1)
            third_pipe = data.find(b'|', second_pipe + 1)
            four_pipe = data.find(b'|', third_pipe + 1)

            header = data[:four_pipe].decode()
            payload = data[four_pipe + 1:]

            header_parts = header.split('|')
            message_type, seq_str, total_str, size = header_parts

            total = int(total_str)

            if message_type == "audio":
                with self.lock:
                    self.audio_buffer.append(payload)
                    if total != self.total_chunks:
                        self.total_chunks = total

            else:
                self.log(f"Mensagem recebida de {addr}: {data.decode(errors='ignore')}")
        except Exception as e:
            self.log(f"Erro ao processar dados: {e}")

    def play_audio_buffer(self):
        while self.is_running:
            if self.audio_buffer:
                with self.lock:
                    buffer_copy = b''.join(self.audio_buffer)
                    self.audio_buffer = []

                # Reproduzir o áudio no buffer
                self.stream.write(buffer_copy)
            else:
                time.sleep(0.01)  # Espera um pouco antes de verificar novamente

    def stop(self):
        self.is_running = False
        self.socket.close()
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

    def log(self, message):
        print(message)


if __name__ == "__main__":
    server = RTPServer()
    server.start()
