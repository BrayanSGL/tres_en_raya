import socket
import threading

class TresEnRayaServer:
    def __init__(self, host, port, buffer_size=2048):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.clients = []
        self.reset_game()

    def reset_game(self):
        self.board = [' ' for _ in range(9)]
        self.turn = 0
        self.game_over = False
        self.winner = ''
        self.draw = False

    def start(self):
        try:
            self.server.bind((self.host, self.port))
            self.server.listen(2)
            print(f"Servidor esperando conexiones en {self.host}:{self.port}")
            while True:
                client, address = self.server.accept()
                print(f"Conexión establecida con {address}")
                self.clients.append(client)
                player = 'O' if len(self.clients) == 1 else 'X'
                client.sendall(player.encode('utf-8'))
                threading.Thread(target=self.handle_client, args=(client,)).start()
        except Exception as e:
            print(str(e))

    def handle_client(self, client):
        while not self.game_over:
            try:
                data = client.recv(self.buffer_size).decode('utf-8')
                if data:
                    self.process_client_message(client, data)
            except Exception as e:
                print(str(e))
                break

    def process_client_message(self, client, message):
        if message == 'reset':
            self.reset_game()
            self.broadcast('reset')
        elif message == 'disconnect':
            self.disconnect_client(client)
        elif message == 'winner':
            self.winner = client.getpeername()
            self.game_over = True
            self.broadcast(f'winner:{self.winner}')
        elif message == 'draw':
            self.draw = True
            self.game_over = True
            self.broadcast('draw')
        else:
            player, move = message.split(':')
            if self.add_move(player, int(move)):
                self.turn += 1
                self.broadcast(f'{player}:{move}')
                if self.check_winner():
                    self.broadcast('winner')
                elif self.turn == 9:
                    self.broadcast('draw')

    def broadcast(self, message):
        for c in self.clients:
            c.sendall(message.encode('utf-8'))

    def disconnect_client(self, client):
        client.close()
        self.clients.remove(client)
        self.broadcast('disconnect')

    def add_move(self, player, move):
        # Verificar si el movimiento es válido
        if self.board[move] == ' ':
            self.board[move] = player
            #borrar consola
            print("\033[H\033[J") 
            print(self.board[0] + '|' + self.board[1] + '|' + self.board[2])
            #separador
            print(self.board[3] + '|' + self.board[4] + '|' + self.board[5])
            #ultimas 3 posiciones
            print(self.board[6] + '|' + self.board[7] + '|' + self.board[8])
            return True
        
        return False
    
    def check_winner(self):
        winning_combinations = [(0, 1, 2), (3, 4, 5), (6, 7, 8),
                                (0, 3, 6), (1, 4, 7), (2, 5, 8),
                                (0, 4, 8), (2, 4, 6)]
        for a, b, c in winning_combinations:
            if self.board[a] == self.board[b] == self.board[c] != ' ':
                print(f"El ganador es {self.board[a]}")
                return True
        return False

if __name__ == "__main__":
    HOST = socket.gethostname()  
    SERVER_IP = socket.gethostbyname(HOST)  
    PORT = 6751  
    BUFFER_SIZE = 2048  

    server = TresEnRayaServer(SERVER_IP, PORT, BUFFER_SIZE)
    server.start()