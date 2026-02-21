import socket
import threading
import json
from PySide6.QtCore import QThread, Signal

rooms = {}

class SocketServer(QThread):
    cliente_conectado = Signal(str)
    cliente_desconectado = Signal(str)
    mensagem_recebida = Signal(dict)

    def __init__(self, host="0.0.0.0", port=8765):
        super().__init__()
        self.host = host
        self.port = port
        self.running = True
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.server.listen()
        self.server.settimeout(1.0)  # permite checar self.running periodicamente
        print(f"Servidor ouvindo em {self.host}:{self.port}")

    def run(self):
        while self.running:
            try:
                conn, addr = self.server.accept()
                self.cliente_conectado.emit(str(addr))
                t = threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True)
                t.start()
            except socket.timeout:
                continue
            except:
                break

    def handle_client(self, conn, addr):
        current_room = None
        buffer = ""
        try:
            while self.running:
                data = conn.recv(4096)
                if not data:
                    break

                buffer += data.decode()
                while "\n" in buffer:
                    raw, buffer = buffer.split("\n", 1)
                    msg = json.loads(raw)
                    action = msg.get("action")

                    # Criar sala (GM)
                    if action == "CREATE_ROOM":
                        room_id = msg["room_id"]
                        rooms[room_id] = [conn]
                        current_room = room_id
                        resp = json.dumps({"action": "ROOM_CREATED", "room_id": room_id}) + "\n"
                        conn.sendall(resp.encode())
                        self.mensagem_recebida.emit(msg)

                    # Entrar em sala
                    elif action == "JOIN_ROOM":
                        room_id = msg["room_id"]
                        if room_id in rooms:
                            rooms[room_id].append(conn)
                            current_room = room_id
                            resp = json.dumps({"action": "ROOM_JOINED", "room_id": room_id}) + "\n"
                            conn.sendall(resp.encode())
                            # avisa o GM que alguem entrou
                            notif = json.dumps({"action": "PLAYER_JOINED", "user": msg.get("user", "?")}) + "\n"
                            self.broadcast(room_id, notif, sender=conn)
                        else:
                            resp = json.dumps({"action": "ERROR", "message": "Sala não encontrada"}) + "\n"
                            conn.sendall(resp.encode())

                    # Chat — repassa para todos na sala incluindo remetente
                    elif action == "CHAT":
                        out = json.dumps({
                            "action": "CHAT",
                            "user": msg.get("user", "?"),
                            "message": msg.get("message", "")
                        }) + "\n"
                        self.broadcast(current_room, out)  # sem sender=conn para incluir quem mandou
                        self.mensagem_recebida.emit(msg)

        except:
            pass

        if current_room and conn in rooms.get(current_room, []):
            rooms[current_room].remove(conn)
        self.cliente_desconectado.emit(str(addr))
        conn.close()

    def broadcast(self, room_id, message, sender=None):
        if room_id in rooms:
            for client in rooms[room_id]:
                if client != sender:
                    try:
                        client.sendall(message.encode())
                    except:
                        pass

    def stop(self):
        self.running = False
        self.server.close()
        self.quit()


if __name__ == "__main__":
    import time
    srv = SocketServer()
    srv.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        srv.stop()