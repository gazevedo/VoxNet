import tkinter as tk
from tkinter import scrolledtext
import threading

from Server.RTCPServer import RTCPServer
from Server.SIPServer import SIPServer
from Server.RTPServer import RTPServer
from Ui.ClientUi import ClientUi


class ServerUi:
    def __init__(self, root):
        self.root = root
        self.root.title("VoIP Server Monitor")

        # Inicialize os servidores, mas não os inicie ainda
        self.sip_server = SIPServer()
        self.rtp_server = RTPServer()
        self.rtcp_server = RTCPServer()

        self.running = False

        # Criação de widgets
        self.create_widgets()

    def create_widgets(self):
        # Área de log
        self.log_area = scrolledtext.ScrolledText(self.root, width=80, height=20, state='disabled')
        self.log_area.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

        # Botões
        self.start_button = tk.Button(self.root, text="Iniciar Servidores", command=self.start_servers)
        self.start_button.grid(row=1, column=0, padx=10, pady=10)

        self.stop_button = tk.Button(self.root, text="Parar Servidores", command=self.stop_servers, state='disabled')
        self.stop_button.grid(row=1, column=1, padx=10, pady=10)

        # Botão para abrir a interface cliente
        self.client_button = tk.Button(self.root, text="Abrir Interface Cliente", command=self.open_client_interface)
        self.client_button.grid(row=2, column=0, padx=10, pady=10, columnspan=2)

        self.open_client_interface()
        self.start_servers()

    def log(self, message):
        """Adiciona uma mensagem à área de log e rola para a parte inferior."""
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, message + '\n')
        self.log_area.config(state='disabled')
        self.log_area.yview(tk.END)

    def start_servers(self):
        """Inicia os servidores em threads separadas."""
        if not self.running:
            self.running = True
            self.log("Iniciando servidores...")
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')

            # Inicie servidores em threads separados
            self.sip_thread = threading.Thread(target=self.sip_server.start, daemon=True)
            self.rtp_thread = threading.Thread(target=self.rtp_server.start, daemon=True)
            self.rtcp_thread = threading.Thread(target=self.rtcp_server.start, daemon=True)

            self.sip_thread.start()
            self.rtp_thread.start()
            self.rtcp_thread.start()

            # Atualize o log com informações de status
            self.log("Servidores iniciados.")

    def stop_servers(self):
        """Para os servidores e fecha os sockets."""
        if self.running:
            self.running = False
            self.log("Parando servidores...")
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')

            # Feche os sockets dos servidores
            self.sip_server.stop()
            self.rtp_server.stop()
            self.rtcp_server.stop()

            self.log("Servidores parados.")

    def open_client_interface(self):
        """Abre a interface cliente em uma nova janela."""
        ClientUi(self.root)
