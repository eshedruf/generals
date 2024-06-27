import socket
import select
import random
import time

class ClientHandler:
    def __init__(self, client_socket, client_address):
        """
        Initialize the ClientHandler object.
        
        Args:
        - client_socket (socket.socket): The socket object representing the client connection.
        - client_address (tuple): The address of the client.
        
        Attributes:
        - client_socket (socket.socket): The socket object representing the client connection.
        - client_address (tuple): The address of the client.
        - connected (bool): Indicates whether the client is still connected.
        """
        self.client_socket = client_socket
        self.client_address = client_address
        self.connected = True
        print(f"New connection from {client_address}")

    def communicate(self):
        """
        Handle communication with the client.
        
        Returns:
        - bool: True if the client is still connected, False otherwise.
        """
        try:
            data = self.client_socket.recv(1024)
            if not data:
                print(f'Client {self.client_address} disconnected')
                self.connected = False
                return False

            number = int(data.decode('utf-8'))
            print(f"Received from {self.client_address}: {number}")
            number += 1
            time.sleep(0.1)  # Sleep for 0.1 seconds
            self.client_socket.sendall(str(number).encode('utf-8'))
            return True
        except Exception as e:
            print(f"Error handling client {self.client_address}: {e}")
            self.connected = False
            return False

    def close(self):
        """
        Close the client socket.
        """
        self.client_socket.close()


class Server:
    def __init__(self, host, port, max_clients):
        """
        Initialize the Server object.

        Args:
        - host (str): The host address on which the server will listen.
        - port (int): The port number on which the server will listen.
        - max_clients (int): The maximum number of clients the server can handle simultaneously.

        Attributes:
        - host (str): The host address on which the server listens.
        - port (int): The port number on which the server listens.
        - max_clients (int): The maximum number of clients the server can handle simultaneously.
        - server_socket (socket.socket): The socket object representing the server.
        - clients (list): A list of ClientHandler objects representing the connected clients.
        """
        self.host = host
        self.port = port
        self.max_clients = max_clients
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []

    def start(self):
        """
        Start the server, bind to the host and port, and begin waiting for clients.
        """
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(self.max_clients)
        print(f'Server listening on {self.host}:{self.port}')

        try:
            self.wait_for_clients()
            print('Reached the maximum number of clients.')
            self.run_game()
        finally:
            self.cleanup()

    def wait_for_clients(self):
        """
        Accept new client connections until the server reaches max_clients.
        Check already connected clients and remove any that have disconnected.
        """
        while len(self.clients) < self.max_clients:
            self._accept_new_clients()
            self._check_connected_clients()

    def run_game(self):
        """
        Handle continuous communication with all connected clients.
        """
        initial_number = random.randint(1, 100)
        for client_handler in self.clients:
            client_handler.client_socket.sendall(str(initial_number).encode('utf-8'))

        try:
            while True:
                readable_sockets = self._get_readable_sockets()
                for client_socket in readable_sockets:
                    client_handler = self._get_client_handler(client_socket)
                    if client_handler:
                        if not client_handler.communicate():
                            self.clients.remove(client_handler)
                            client_handler.close()
                            self.print_client_stats()
        except Exception as e:
            print(f"Error in communication: {e}")

    def _accept_new_clients(self):
        """
        Accept new client connections if the server is not at maximum capacity.
        """
        readable, _, _ = select.select([self.server_socket], [], [], 1)
        if self.server_socket in readable:
            client_socket, client_address = self.server_socket.accept()
            if len(self.clients) < self.max_clients:
                client_handler = ClientHandler(client_socket, client_address)
                self.clients.append(client_handler)
                self.print_client_stats()
            else:
                client_socket.close()
                print('Max clients reached, rejecting new connection.')

    def _check_connected_clients(self):
        """
        Check all connected clients and remove any that have disconnected.
        """
        for client_handler in self.clients[:]:
            if not self._is_client_connected(client_handler.client_socket):
                self.clients.remove(client_handler)
                client_handler.close()
                self.print_client_stats()

    def _is_client_connected(self, client_socket):
        """
        Check if a client is still connected.

        Args:
        - client_socket (socket.socket): The socket object representing the client connection.

        Returns:
        - bool: True if the client is still connected, False otherwise.
        """
        try:
            # Send a non-blocking zero-byte message to check if the socket is still connected
            client_socket.send(b'')
            return True
        except:
            return False

    def _get_readable_sockets(self):
        """
        Get the list of sockets that are ready for reading.

        Returns:
        - list: List of sockets that are ready for reading.
        """
        client_sockets = [client.client_socket for client in self.clients]
        readable, _, _ = select.select(client_sockets, [], [], 1)
        return readable

    def _get_client_handler(self, client_socket):
        """
        Find the ClientHandler associated with a given client socket.

        Args:
        - client_socket (socket.socket): The socket object representing the client connection.

        Returns:
        - ClientHandler: The ClientHandler object associated with the client socket.
        """
        for client_handler in self.clients:
            if client_handler.client_socket is client_socket:
                return client_handler
        return None

    def cleanup(self):
        """
        Clean up resources by closing the server socket and all client sockets.
        """
        self.server_socket.close()
        for client_handler in self.clients:
            client_handler.close()

    def print_client_stats(self):
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
