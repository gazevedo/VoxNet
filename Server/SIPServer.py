import socket

class SIPServer:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('localhost', 5060))
        print("SIP Server iniciado na porta 5060.")

    def start(self):
        while True:
            data, addr = self.socket.recvfrom(1024)  # Tamanho do buffer ajustado
            self.handle_data(data, addr)

    def handle_data(self, data, addr):
        try:
            # Processamento do pacote SIP
            self.log(f"SIP recebido de {addr}: {data.decode(errors='ignore')}")
        except Exception as e:
            self.log(f"Erro ao processar dados: {e}")

    def log(self, message):
        print(message)

    def stop(self):
        self.socket.close()

if __name__ == "__main__":
    server = SIPServer()
    server.start()
