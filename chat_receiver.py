import socket
import random

# Configurações
HOST = "0.0.0.0"       # Escuta todas as interfaces de rede
PORT = 5001            # Porta padrão 
DROP_RATE = 0.4        # 40% de perda no canal


def run_chat_receiver():
    # Socket UDP
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((HOST, PORT))
        print(f"=== [Chat Server] Online na porta {PORT}... ===")

        while True:
            # Tamanho máximo de buffer
            data, addr = s.recvfrom(1024)

            # Perda no canal não confiável
            if random.random() < DROP_RATE:
                print("=== [CANAL] Pacote descartado! ===")
                continue

            raw_message = data.decode("utf-8")

            # Permitir que o usuário digite "|" no input
            parts = raw_message.split("|", 2)

            if len(parts) == 3 and parts[0] == "MSG":
                msg_id = parts[1]
                msg_text = parts[2]

                # Exibe a mensagem recebida com seu id
                print(f"=== [Recebido de {addr}] MSG ID {msg_id}: {msg_text} ===")

                # Devolve a confirmação para o remetente
                ack_packet = f"DELIVERED|{msg_id}".encode("utf-8")
                s.sendto(ack_packet, addr)
            else:
                # Descarta pacotes que não sigam o protocolo
                print(f"=== [Aviso] Datagrama fora do padrão ignorado de {addr}: {raw_message} ===")


if __name__ == "__main__":
    run_chat_receiver()