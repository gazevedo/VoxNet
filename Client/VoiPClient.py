import socket


class VoiPClient:
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
                return "Tipo de mensagem não suportado"

            # Envia a mensagem para o endereço especificado
            sock.sendto(formatted_message, address)
            return f"Enviado para {address}: {formatted_message[:50]}..."

        except Exception as e:
            return f"Erro ao enviar mensagem: {e}"
        finally:
            sock.close()