import socket
import time
from shared.protocol import *
from shared.map import *
from constants.protocol import *

class Client:
    def __init__(self, host, port, map):
        self.host = host
        self.port = port
        self.map = map
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # not used
    def start(self):
        self.connect()
        print("Connected to the server")

        try:
            while True:
                msg_type, content = Protocol.get_message(self.client_socket)
                if content and content != "":
                    print(content)
                    Protocol.handle_msg(msg_type, content, self.map)

                time.sleep(100000000)  # Adjust the sleep duration as needed
        except KeyboardInterrupt:
            print("Client disconnected by user")
        finally:
            self.client_socket.close()
        
    def connect(self):
        self.client_socket.connect((self.host, self.port))
        return True

    def send_action(self, from_x, from_y, to_x, to_y):
        msg = Protocol.create_action_msg(from_x, from_y, to_x, to_y)
        self.client_socket.sendall(msg.encode('utf-8'))


if __name__ == "__main__":
    HOST = '127.0.0.99'
    PORT = 12345
    map = Map()
    client = Client(HOST, PORT, map)
    client.connect()