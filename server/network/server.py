import socket
import select
import time

from shared.protocol import *
from shared.map import *

from constants.server import *

class ClientHandler:
    def __init__(self, client_socket, client_address):
        self.socket = client_socket
        self.address = client_address

    def is_connected(self):
        try:
            self.socket.setblocking(0)
            data = self.socket.recv(1, socket.MSG_PEEK)
            if data == b'':
                return False
            return True
        except BlockingIOError:
            return True
        except socket.error:
            return False

    def close(self):
        self.socket.close()

class Server:
    def __init__(self, host, port, map, num_players=2):
        self.host = host
        self.port = port
        self.map = map
        self.num_players = num_players
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []
        self.kings = []

    def start(self):
        self._setup_server_socket()
        self._accept_and_check_clients()
        self._initialize_game()
        self._run_game_loop()

    def _setup_server_socket(self):
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(self.num_players)

    def _accept_and_check_clients(self):
        try:
            while len(self.clients) < self.num_players:
                self._accept_new_clients()
                self._check_connected_clients()
        except Exception as e:
            self.cleanup()
            raise e

    def _initialize_game(self):
        self.map.generate_new(self.num_players)
        self._find_kings()

    def _run_game_loop(self):
        turn_counter = 0
        try:
            while True:
                self._send_map_updates()
                self._handle_client_messages()
                self._update_armies(turn_counter)
                turn_counter = (turn_counter + 1) % TURNS_TO_RESET
                time.sleep(0.2)
        except (BrokenPipeError, ValueError):
            self.cleanup()

    def _send_map_updates(self):
        for client in self.clients:
            map_msg = Protocol.create_map_msg(self.map, self.clients.index(client) + 1)
            client.socket.sendall(map_msg.encode('utf-8'))

    def _handle_client_messages(self):
        client_sockets = [client.socket for client in self.clients]
        readable, _, _ = select.select([self.server_socket] + client_sockets, [], [], 0.2)
        for s in readable:
            msg_type, content = Protocol.get_message(s)
            if content:
                Protocol.handle_msg(msg_type, content, self.map, client_sockets=client_sockets, s=s)

    def _update_armies(self, turn_counter):
        for y in range(ROWS):
            for x in range(COLS):
                tile = self.map.tiles[y][x]
                if turn_counter == 0 and tile.type == ARMY and tile.owner > 0:
                    tile.army += 1
                elif tile.type in (KING, CITY) and tile.owner > 0:
                    tile.army += 1

    def _accept_new_clients(self):
        readable, _, _ = select.select([self.server_socket], [], [], 1)
        if self.server_socket in readable:
            client_socket, client_address = self.server_socket.accept()
            if len(self.clients) < self.num_players:
                self.clients.append(ClientHandler(client_socket, client_address))
            else:
                client_socket.close()

    def _check_connected_clients(self):
        for client in self.clients[:]:
            if not client.is_connected():
                client.close()
                self.clients.remove(client)

    def _find_kings(self):
        for y in range(ROWS):
            for x in range(COLS):
                tile = self.map.tiles[y][x]
                if tile.type == KING:
                    self.kings.append((x, y))

    def get_ip(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('8.8.8.8', 1))
            ip = s.getsockname()[0]
        return ip

    def cleanup(self):
        self.server_socket.close()
        for client in self.clients:
            client.close()
