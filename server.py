import socket
import select
from random import randint

class Server:
    def __init__(self) -> None:
        self.host = "0.0.0.0"
        self.port = randint(1024, 9999)
        self.max_connections = 2
        self.server_socket = None
        self.inputs = []  # used by select.select()
        self.connected_clients = set()  # exists only to monitor the NUMBER of connected clients and nothing more (for now)

    def get_ip(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('8.8.8.8', 1))
            ip = s.getsockname()[0]
        return ip

    def _init_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        #print(f"Server listening on {self.host}:{self.port}")

        self.inputs = [self.server_socket]

    def _accept_new_connection(self):
        client_socket, client_address = self.server_socket.accept()
        #print(f"Client {client_address} connected.")
        self.inputs.append(client_socket)
        self.connected_clients.add(client_socket)

        # check if reached the desired number of connected clients
        if len(self.connected_clients) == self.max_connections:
            # THIS IS WRONG, THE SERVER SHOULD NOT BE CLOSED. WILL BE CHANGED LATER.
            #print(f"{self.max_connections} clients are now connected: stopping the server.")
            self.server_socket.close()
            return False
        return True

    def _handle_readable_socket(self, s):
        data = s.recv(1024)
        if data:
            #print(f"Received data from {s.getpeername()}: {data.decode()}")
            pass
        else:
            self._handle_disconnection(s)

    def _handle_disconnection(self, s):
        #print(f"Client {s.getpeername()} disconnected.")
        self.inputs.remove(s)
        self.connected_clients.remove(s)
        s.close()

    def start(self):
        self._init_server()

        while True:
            readable, _, _ = select.select(self.inputs, [], [])

            for s in readable:
                if s is self.server_socket:
                    if not self._accept_new_connection():
                        return
                else:
                    self._handle_readable_socket(s)

