import socket
import threading

# Configurações
TARGET_IP = "127.0.0.1"   # Endereço loopback
PORT = 5001

# Controle de estado de mensagens pendentes
pending_messages = {}
msg_counter = 1

lock = threading.Lock()

def listen_receipts(sock):
    """
    Thread em segundo plano (DELIVERED|<ID>)
    sem bloquear a mensagem do usuário
    """
    while True:
        try:
            data, _ = sock.recvfrom(1024)
            raw = data.decode("utf-8")

            # Parsing do recibo de entrega
            parts = raw.split("|", 1)
            if len(parts) == 2 and parts[0] == "DELIVERED":
                try:
                    msg_id = int(parts[1])
                except ValueError:
                    continue

                with lock:
                    if msg_id in pending_messages:
                        texto = pending_messages.pop(msg_id)
                        print(
                            f"\n[Entregue (Check Azul)] MSG {msg_id} ('{texto}') confirmada!\n> ",
                            end="",
                            flush=True
                        )
        except Exception:
            break


def run_chat_sender():
    global msg_counter

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        listener = threading.Thread(target=listen_receipts, args=(s,), daemon=True)
        listener.start()

        print("=== Chat UDP ===")
        print("Comandos:")
        print("  /status   -> Mensagens pendentes")
        print("  /reenviar -> Reenvia mensagens pendentes\n")

        while True:
            try:
                user_input = input("> ").strip()
                if not user_input:
                    continue

                # Comando /status: lista mensagens que ainda não receberam o ACK
                if user_input == "/status":
                    with lock:
                        if not pending_messages:
                            print("[Status] Todas as mensagens foram confirmadas")
                        else:
                            print(f"[Status] {len(pending_messages)} mensagem(ns) pendente(s):")
                            for mid, txt in sorted(pending_messages.items()):
                                print(f"  - ID {mid}: {txt}")
                    continue

                # Comando /reenviar: retransmite pendências
                if user_input == "/reenviar":
                    with lock:
                        if not pending_messages:
                            print("[Reenvio] Nenhuma mensagem pendente no momento.")
                        else:
                            print(f"[Reenvio] Reenviando {len(pending_messages)} mensagem(ns) pendente(s)...")
                            for mid, txt in pending_messages.items():
                                packet = f"MSG|{mid}|{txt}".encode("utf-8")
                                s.sendto(packet, (TARGET_IP, PORT))
                    continue

                # Envio de nova mensagem
                with lock:
                    current_id = msg_counter
                    pending_messages[current_id] = user_input
                    msg_counter += 1

                packet = f"MSG|{current_id}|{user_input}".encode("utf-8")
                s.sendto(packet, (TARGET_IP, PORT))
                print(f"[Pendente (Check Cinza)] MSG {current_id} enviada.")

            except KeyboardInterrupt:
                print("\nEncerrando chat...")
                break


if __name__ == "__main__":
    run_chat_sender()