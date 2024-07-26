import threading

from Server.RTCPServer import RTCPServer
from Server.RTPServer import RTPServer
from Server.SIPServer import SIPServer


class VoIPServer:
    def __init__(self, sip_host='0.0.0.0', sip_port=5060,
                 rtp_host='0.0.0.0', rtp_port=5004,
                 rtcp_host='0.0.0.0', rtcp_port=5005):
        self.sip_server = SIPServer(host=sip_host, port=sip_port)
        self.rtp_server = RTPServer(host=rtp_host, port=rtp_port)
        self.rtcp_server = RTCPServer(host=rtcp_host, port=rtcp_port)
        self.active_sessions = {}

    def start(self):
        threading.Thread(target=self.sip_server.start, daemon=True).start()
        threading.Thread(target=self.rtp_server.start, daemon=True).start()
        threading.Thread(target=self.rtcp_server.start, daemon=True).start()

    def handle_sip_message(self, message, address):
        if "INVITE" in message:
            self.handle_invite(message, address)
        elif "BYE" in message:
            self.handle_bye(message, address)
        elif "REGISTER" in message:
            self.handle_register(message, address)
        else:
            response = "SIP/2.0 400 Bad Request"
            self.sip_server.send_response(response, address)

    def handle_invite(self, message, address):
        session_id = self.create_session(address)
        response = f"SIP/2.0 200 OK\nSession-ID: {session_id}"
        self.sip_server.send_response(response, address)
        self.configure_rtp_rtcp(session_id)
        print(f"INVITE processado, sessão criada: {session_id}")

    def handle_bye(self, message, address):
        session_id = self.extract_session_id(message)
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            response = "SIP/2.0 200 OK"
            self.sip_server.send_response(response, address)
            print(f"BYE processado, sessão encerrada: {session_id}")
        else:
            response = "SIP/2.0 404 Not Found"
            self.sip_server.send_response(response, address)

    def handle_register(self, message, address):
        response = "SIP/2.0 200 OK"
        self.sip_server.send_response(response, address)
        print("REGISTER processado")

    def create_session(self, address):
        session_id = len(self.active_sessions) + 1
        self.active_sessions[session_id] = {
            'address': address,
            'rtp_port': 5004,  # Exemplo, pode ser dinâmico
            'rtcp_port': 5005  # Exemplo, pode ser dinâmico
        }
        return session_id

    def configure_rtp_rtcp(self, session_id):
        # Configura Server e RTCP para a nova sessão
        session = self.active_sessions.get(session_id)
        if session:
            # Configure Server
            rtp_port = session['rtp_port']
            # Adicione lógica para configurar o servidor Server para a nova sessão

            # Configure RTCP
            rtcp_port = session['rtcp_port']
            # Adicione lógica para configurar o servidor RTCP para a nova sessão
            print(f"RTP e RTCP configurados para a sessão {session_id}")

    def extract_session_id(self, message):
        lines = message.split("\n")
        for line in lines:
            if line.startswith("Session-ID:"):
                return int(line.split(":")[1].strip())
        return None
