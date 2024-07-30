import socket
import time
from shared.protocol import *
from shared.map import *
from constants.protocol import *

class Client:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.map = map
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
    def connect(self):
        self.client_socket.connect((self.ip, self.port))
        return True

    def send_action(self, from_x, from_y, to_x, to_y):
        msg = Protocol.create_action_msg(from_x, from_y, to_x, to_y)
        self.client_socket.sendall(msg.encode('utf-8'))

    def check_connected(self):
        try:
            self.client_socket.send(b'')
            return True
        except socket.error:
            return False
