import socket
import json


class ChessClient:
    def __init__(self, host='127.0.0.1', port=65432):
        self.host = host
        self.port = port
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect_to_server(self):
        try:
            self.conn.connect((self.host, self.port))
            print("Connected to the server")
        except ConnectionRefusedError:
            print("Server is not available")

    def send_move(self, move):
        try:
            # Кодируем ход в JSON формат
            move_data = json.dumps(move)
            # Отправляем ход на сервер
            self.conn.sendall(move_data.encode('utf-8'))
        except Exception as e:
            print(f"Failed to send move: {e}")

    def receive_move(self):
        try:
            # Получаем ход от сервера
            move_data = self.conn.recv(1024)
            if not move_data:
                print("No data received")
                return None

            # Декодируем JSON формат в Python объект
            move = json.loads(move_data.decode('utf-8'))
            return move
        except Exception as e:
            print(f"Failed to receive move: {e}")
            return None
