import socket
import select
import random
import time

from shared.protocol import *
from shared.map import *

from constants.server import *

class Server:
    def __init__(self, host, port, map, num_players):
        self.host = host
        self.port = port
        self.map = map
        self.num_players = num_players
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []
        self.connected_clients = len(self.clients)
        self.id_list = [_ for _ in range(1, self.num_players+1)]
        self.kings = []

    def start(self):
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(self.num_players)
        #print(f'Server listening on {self.host}:{self.port}')

        try:
            while len(self.clients) < self.num_players:
                self._accept_new_clients()
                self._check_connected_clients()
            self.map.generate_new(self.num_players)

            for y in range(ROWS):
                for x in range(COLS):
                    tile = self.map.tiles[y][x]
                    if tile.type == KING:
                        self.kings.append((x, y))
            #print('Reached the maximum number of clients.')

            gen_counter = 0
            while True:
                # Create and send the map message after updating the army values
                for s in self.clients:
                    map_msg = Protocol.create_map_msg(self.map, self.clients.index(s)+1)
                    s.sendall(map_msg.encode('utf-8'))

                readable, _, _ = select.select(self.clients, [], [], 0.2)
                for s in readable:
                    msg_type, content = Protocol.get_message(s)
                    if content and content != "":
                        Protocol.handle_msg(msg_type, content, self.map, clients=self.clients, s=s)

                # Update army values first
                for y in range(ROWS):
                    for x in range(COLS):
                        tile = self.map.tiles[y][x]
                        if gen_counter >= GEN_TO_RESET and tile.type == ARMY and tile.owner > 0:
                            tile.army += 1
                        elif tile.type == KING or (tile.type == CITY and tile.owner > 0):
                            tile.army += 1

                if gen_counter >= GEN_TO_RESET:
                    gen_counter = 0
                else:
                    gen_counter += 1
                time.sleep(0.8)
                

        
        except (BrokenPipeError, ValueError):
            s.close()

        finally:
            self.cleanup()

    def get_ip(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('8.8.8.8', 1))
            ip = s.getsockname()[0]
        return ip

    def _accept_new_clients(self):
        readable, _, _ = select.select([self.server_socket], [], [], 1)
        if self.server_socket in readable:
            client_socket, client_address = self.server_socket.accept()
            if len(self.clients) < self.num_players:
                self.clients.append(client_socket)
                self.print_client_stats()
            else:
                client_socket.close()
                print('Max clients reached, rejecting new connection.')

    def _check_connected_clients(self):
        for client_socket in self.clients:
            if not self._is_client_connected(client_socket):
                self.clients.remove(client_socket)
                client_socket.close()
                self.print_client_stats()

    def _is_client_connected(self, client_socket):
        try:
            # Send a non-blocking zero-byte message to check if the socket is still connected
            client_socket.send(b'')
            return True
        except:
            return False

    def _get_readable_sockets(self):
        client_sockets = [client.client_socket for client in self.clients]
        readable, _, _ = select.select(client_sockets, [], [], 1)
        return readable

    def _get_client_handler(self, client_socket):
        for client_handler in self.clients:
            if client_handler.client_socket is client_socket:
                return client_handler
        return None

    def cleanup(self):
        self.server_socket.close()
        for client_handler in self.clients:
            client_handler.close()

    def print_client_stats(self):
        current_connections = len(self.clients)
        #print(f'Current connections: {current_connections}/{self.num_players}')

if __name__ == "__main__":
    num_players = 2
    map = Map()
    server = Server('127.0.0.99', 12345, map, num_players)

    server.start()
