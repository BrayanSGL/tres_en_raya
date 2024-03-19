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
            self.board = message.split(':') # Ejemplo: 'X:4'
            self.turn = (self.turn + 1) % 2 # Cambiar de turno
            self.broadcast(message) # Enviar el movimiento a los clientes

    def broadcast(self, message):
        for c in self.clients:
            c.sendall(message.encode('utf-8'))

    def disconnect_client(self, client):
        client.close()
        self.clients.remove(client)
        self.broadcast('disconnect')

if __name__ == "__main__":
    HOST = socket.gethostname()  
    SERVER_IP = socket.gethostbyname(HOST)  
    PORT = 6751  
    BUFFER_SIZE = 2048  

    server = TresEnRayaServer(SERVER_IP, PORT, BUFFER_SIZE)
    server.start()