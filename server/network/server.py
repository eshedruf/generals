import socket
import select
import time

from shared.protocol import *
from shared.map import *

from constants.server import *
from constants.server import *

class Server:
    def __init__(self, host, port, map, num_players=2):
        self.host = host
        self.port = port
        self.map = map
        self.num_players = num_players
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = {} # map the client address to socket
        self.kings = []

    def start(self):
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(self.num_players)

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

            gen_counter = 0
            while True:
                client_sockets = list(self.clients.values())
                # Create and send the map message after updating the army values
                for s in client_sockets:
                    map_msg = Protocol.create_map_msg(self.map, client_sockets.index(s) + 1)
                    s.sendall(map_msg.encode('utf-8'))

                readable, _, _ = select.select([self.server_socket] + client_sockets, [], [], 0.2)
                for s in readable:
                    msg_type, content = Protocol.get_message(s)
                    if content and content != "":
                        Protocol.handle_msg(msg_type, content, self.map, client_sockets=client_sockets, s=s)

                # Update army values first
                for y in range(ROWS):
                    for x in range(COLS):
                        tile = self.map.tiles[y][x]
                        if gen_counter >= TURNS_TO_RESET and tile.type == ARMY and tile.owner > 0:
                            tile.army += 1
                        elif tile.type == KING or (tile.type == CITY and tile.owner > 0):
                            tile.army += 1

                if gen_counter >= TURNS_TO_RESET:
                    gen_counter = 0
                else:
                    gen_counter += 1
                time.sleep(0.2)

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
                self.clients[client_address] = client_socket
            else:
                client_socket.close()

    def _check_connected_clients(self):
        keys_to_remove = []
        for client_address, client_socket in self.clients.items():
            if not self._is_client_connected(client_socket):
                keys_to_remove.append(client_address)
                client_socket.close()

        for key in keys_to_remove:
            del self.clients[key]
        

    def _is_client_connected(self, client_socket):
        try:
            # Use the MSG_PEEK flag to check for data without removing it from the buffer
            client_socket.setblocking(0)
            data = client_socket.recv(1, socket.MSG_PEEK)
            if data == b'':
                return False
            return True
        except BlockingIOError:
            return True
        except socket.error:
            return False

    def cleanup(self):
        self.server_socket.close()
        for client_socket in self.clients.values():
            client_socket.close()


