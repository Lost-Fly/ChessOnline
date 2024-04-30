import socket
import threading
import time


class ChessServer:
    def __init__(self, host='192.168.170.249', port=65432):
        self.host = host
        self.port = port
        self.clients = []
        self.matches = {}

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            print(f"Server started and listening on {self.host}:{self.port}")
            try:
                while True:
                    conn, addr = s.accept()
                    print(f"Connected by {addr}")
                    self.clients.append(conn)
                    if len(self.clients) == 1:
                        time.sleep(2)
                        white_player = self.clients[0]
                        white_player.sendall(b'white')
                        print("send w color")

                    if len(self.clients) % 2 == 0:
                        white_player = self.clients[-2]
                        black_player = self.clients[-1]
                        # Отправка цветов игрокам
                        time.sleep(10)
                        # white_player.sendall(b'white')
                        # print("send w color")
                        black_player.sendall(b'black')
                        print("send b color")
                        match_id = len(self.matches)
                        self.matches[match_id] = (white_player, black_player)
                        threading.Thread(target=self.handle_match, args=(match_id,)).start()
            except KeyboardInterrupt:
                print("Server is shutting down.")

    def handle_match(self, match_id):
        player1_conn, player2_conn = self.matches[match_id]
        try:
            while True:
                for player_conn in [player1_conn, player2_conn]:
                    move_msg = player_conn.recv(1024)

                    print(move_msg.decode('utf-8'))

                    if not move_msg:
                        print(f"Player disconnected from match ID {match_id}")
                        self.close_match(match_id)
                        return

                    opponent_conn = player2_conn if player_conn is player1_conn else player1_conn
                    opponent_conn.sendall(move_msg)

                    if move_msg.decode('utf-8').lower() in ('mate', 'stalemate', 'resign'):
                        print(f"Game over in match ID {match_id}")
                        self.close_match(match_id)
                        return
        except Exception as e:
            print(f"Exception occurred in match {match_id}: {e}")
            self.close_match(match_id)

    def close_match(self, match_id):
        if match_id in self.matches:
            player1_conn, player2_conn = self.matches[match_id]
            player1_conn.close()
            player2_conn.close()
            del self.matches[match_id]
            self.clients.remove(player1_conn)
            self.clients.remove(player2_conn)
            print(f"Match ID {match_id} closed")


if __name__ == "__main__":
    server = ChessServer()
    server.start()
