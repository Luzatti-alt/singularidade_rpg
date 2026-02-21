from PySide6.QtCore import QThread, Signal
import socket
import json

class SocketClient(QThread):
    message_received = Signal(dict)

    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.running = True
        self.buffer = ""

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.host, self.port))

    def run(self):
        while self.running:
            try:
                data = self.client.recv(4096)
                if not data:
                    break

                self.buffer += data.decode()

                while "\n" in self.buffer:
                    message, self.buffer = self.buffer.split("\n", 1)
                    msg = json.loads(message)
                    self.message_received.emit(msg)

            except:
                break

    def send_json(self, data):
        message = json.dumps(data) + "\n"
        self.client.sendall(message.encode())

    def stop(self):
        self.running = False
        self.client.close()
        self.quit()