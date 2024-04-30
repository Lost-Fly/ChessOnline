import socket
import json


class ChessClient:
    def __init__(self, host='192.168.170.249', port=65432):
        self.host = host
        self.port = port
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect_to_server(self):
        try:
            self.conn.connect((self.host, self.port))
            # print(self.receive_move())
            print("Connected to the server")
        except ConnectionRefusedError:
            print("Server is not available")

    def is_connected(self):
        try:
            self.conn.getpeername()
            return True
        except:
            return False

    def send_move(self, move):
        try:
            move_data = json.dumps(move)

            print("SEND DATA CAST TO JSON" + move_data)

            self.conn.sendall(move_data.encode('utf-8'))
        except Exception as e:
            print(f"Failed to send move: {e}")

    def receive_move(self):
        try:
            move_data = self.conn.recv(1024)
            if not move_data:
                print("No data received")
                return None

            print("RECEIVE DATA BEFORE CAST TO JSON" + move_data.decode('utf-8'))

            if move_data.decode('utf-8') == "white" or move_data.decode('utf-8') == "black":
                return move_data.decode('utf-8')

            move = json.loads(move_data.decode('utf-8'))

            return move

        except Exception as e:
            return None
