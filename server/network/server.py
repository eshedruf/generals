import socket
import select
import time

from shared.protocol import *
from shared.map import *

from constants.server import *

class ClientHandler:
    def __init__(self, client_socket, client_address, client_id):
        self.socket = client_socket
        self.address = client_address
        self.id = client_id

    def is_connected(self):
        if self.socket is None:
            return False
        try:
            self.socket.setblocking(0)
            data = self.socket.recv(1, socket.MSG_PEEK)
            return data != b''
        except BlockingIOError:
            return True
        except socket.error:
            return False

    def send_message(self, message):
        if self.socket is None:
            return
        try:
            self.socket.sendall(message.encode('utf-8'))
        except (BrokenPipeError, ValueError):
            self.socket.close()
            self.socket = None

class Server:
    def __init__(self, host, port, game_map, num_players=2):
        self.host = host
        self.port = port
        self.map = game_map
        self.num_players = num_players
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = [] # list of ClientHandler
        self.kings = []

    def start(self):
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(self.num_players)

        try:
            self._accept_clients_until_ready()
            self.map.generate_new(self.num_players)
            self._initialize_kings()

            gen_counter = 0
            while True:
                self._send_map_updates()
                self._handle_client_messages()
                self._check_new_connections()
                self._update_armies(gen_counter)
                gen_counter = (gen_counter + 1) % (TURNS_TO_RESET + 1)
                time.sleep(0.2)
        except (BrokenPipeError, ValueError) as e:
            print(f"Error: {e}")
        finally:
            self.cleanup()

    def get_ip(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('8.8.8.8', 1))
            return s.getsockname()[0]

    def _accept_clients_until_ready(self):
        client_id = 1
        while len(self.clients) < self.num_players:
            self._accept_new_clients(client_id)
            self._check_connected_clients()
            client_id += 1

    def _accept_new_clients(self, client_id):
        readable, _, _ = select.select([self.server_socket], [], [], 1)
        if self.server_socket in readable:
            client_socket, client_address = self.server_socket.accept()
            if len(self.clients) < self.num_players:
                handler = ClientHandler(client_socket, client_address, client_id)
                self.clients.append(handler)
            else:
                client_socket.close()

    def _check_connected_clients(self):
        for handler in self.clients:
            if not handler.is_connected():
                handler.socket.close()
                handler.socket = None

    def _check_new_connections(self):
        readable, _, _ = select.select([self.server_socket], [], [], 0.2)
        if self.server_socket in readable:
            client_socket, client_address = self.server_socket.accept()
            existing_client = next((handler for handler in self.clients if handler.address == client_address), None)
            if existing_client:
                existing_client.socket.close()
                existing_client.socket = client_socket
            else:
                client_socket.close()

    def _initialize_kings(self):
        for y in range(ROWS):
            for x in range(COLS):
                if self.map.tiles[y][x].type == KING:
                    self.kings.append((x, y))

    def _send_map_updates(self):
        for handler in self.clients:
            if handler.socket:
                map_msg = Protocol.create_map_msg(self.map, handler.id)
                handler.send_message(map_msg)

    def _handle_client_messages(self):
        client_sockets = [handler.socket for handler in self.clients if handler.socket]
        readable, _, _ = select.select([self.server_socket] + client_sockets, [], [], 0.2)
        for s in readable:
            if s is not self.server_socket:
                msg_type, content = Protocol.get_message(s)
                if content:
                    Protocol.handle_msg(msg_type, content, self.map, client_sockets=client_sockets, s=s)

    def _update_armies(self, gen_counter):
        for y in range(ROWS):
            for x in range(COLS):
                tile = self.map.tiles[y][x]
                if gen_counter >= TURNS_TO_RESET and tile.type == ARMY and tile.owner > 0:
                    tile.army += 1
                elif tile.type in {KING, CITY} and tile.owner > 0:
                    tile.army += 1

    def cleanup(self):
        self.server_socket.close()
        for handler in self.clients:
            if handler.socket:
                handler.socket.close()
