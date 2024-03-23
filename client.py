import socket

class TresEnRayaClient:
    def __init__(self, host, port, buffer_size=2048):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.player = None

    def connect(self):
        self.client.connect((self.host, self.port))
        self.player = self.client.recv(self.buffer_size).decode('utf-8')
        print(f"Soy el jugador: {self.player}")

    def send_message(self, message):
        self.client.sendall(message.encode('utf-8'))

    def receive_message(self):
        return self.client.recv(self.buffer_size).decode('utf-8')

    def disconnect(self):
        self.client.close()

if __name__ == "__main__":
    HOST = '192.168.20.14'  # Cambiar a la dirección IP del servidor si es necesario
    PORT = 6751  
    BUFFER_SIZE = 2048  

    client = TresEnRayaClient(HOST, PORT, BUFFER_SIZE)
    client.connect()

    while True:
        move = input("Ingrese su movimiento (0-8): ")
        client.send_message(f"{client.player}:{move}")
        response = client.receive_message()
        print(response)

        if "winner" in response or "draw" in response:
            break

    client.disconnect()