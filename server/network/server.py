import socket
import select
import time
import random

class Server:
    def __init__(self, host, port, max_clients):
        """
        Initialize the Server object.

        Args:
        - host (str): The host address on which the server will listen.
        - port (int): The port number on which the server will listen.
        - max_clients (int): The maximum number of clients the server can handle simultaneously.
        """
        self.host = host
        self.port = port
        self.max_clients = max_clients
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []

    def start(self):
        """
        Start the server, listen for incoming connections, handle client interactions,
        and start continuous communication with clients.
        """
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(self.max_clients)
        print(f'Server listening on {self.host}:{self.port}')

        try:
            # Accept connections until reaching max_clients
            while len(self.clients) < self.max_clients:
                self._handle_connections()

            print('Reached the maximum number of clients.')

            # Send initial random number to each client
            initial_number = random.randint(1, 100)
            for client_socket in self.clients:
                client_socket.sendall(str(initial_number).encode('utf-8'))

            # Start continuous communication with clients
            self._start_communication()

        finally:
            self._cleanup()

    def _handle_connections(self):
        """
        Use select to wait for incoming connections or I/O events on sockets.
        """
        readable, _, _ = select.select([self.server_socket] + self.clients, [], [], 1)
        
        for s in readable:
            if s is self.server_socket:
                self._accept_new_connection()
            else:
                self._handle_client(s)

    def _accept_new_connection(self):
        """
        Accept a new client connection and add it to the list of clients,
        if not already at maximum capacity.
        """
        if len(self.clients) < self.max_clients:
            client_socket, client_address = self.server_socket.accept()
            print(f'New connection from {client_address}')
            self.clients.append(client_socket)
            self._print_client_stats()
        else:
            # If max_clients is reached, reject the new connection
            client_socket, _ = self.server_socket.accept()
            client_socket.close()
            print('Max clients reached, rejecting new connection.')

    def _handle_client(self, client_socket):
        """
        Handle communication with a client.
        
        Args:
        - client_socket (socket.socket): The socket object representing the client connection.
        """
        data = client_socket.recv(1024)
        if not data:
            print(f'Client {client_socket.getpeername()} disconnected')
            self.clients.remove(client_socket)
            client_socket.close()
            self._print_client_stats()
        else:
            number = int(data.decode('utf-8'))
            print(f"Received from {client_socket.getpeername()}: {number}")
            number += 1
            time.sleep(0.1)  # Sleep for 0.1 seconds
            client_socket.sendall(str(number).encode('utf-8'))

    def _start_communication(self):
        """
        Start continuous communication with all connected clients.
        """
        try:
            while True:
                self._handle_connections()

        except Exception as e:
            print(f"Error in communication: {e}")

    def _cleanup(self):
        """
        Clean up resources by closing the server socket and all client sockets.
        """
        self.server_socket.close()
        for client_socket in self.clients:
            client_socket.close()

    def _print_client_stats(self):
        """
        Print current number of connected clients and maximum allowed clients.
        """
        current_connections = len(self.clients)
        print(f'Current connections: {current_connections}/{self.max_clients}')

if __name__ == "__main__":
    HOST = '127.0.0.99'
    PORT = 12345
    MAX_CLIENTS = 1

    server = Server(HOST, PORT, MAX_CLIENTS)
    server.start()
