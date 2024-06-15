import socket
import threading

class Client:
    def __init__(self, host, port):
        """
        host: the server's IP address
        port: the server's port
        afaik it works.
        """
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        self.receive_thread = None

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        print(f"Connected to server at {self.host}:{self.port}")
        self.running = True

        # Start a thread to continuously receive messages from the server
        self.receive_thread = threading.Thread(target=self._receive_messages)
        self.receive_thread.start()

    def _receive_messages(self):
        while self.running:
            try:
                data = self.socket.recv(1024)
                if not data:
                    break
                print("Received from server:", data.decode())
            except Exception as e:
                print("Error receiving data from server:", e)
                break
        self.socket.close()
        self.running = False

    def send_message(self, message):
        if self.socket:
            self.socket.sendall(message.encode())
        else:
            print("Error: Client not connected.")

    def close(self):
        if self.socket:
            self.socket.close()
        else:
            print("Error: Client not connected.")

def main():
    # Example usage
    client = Client('192.168.0.113', 1302)
    client.connect()

    # Continuously send messages until the program is terminated
    while client.running:
        message = input("Enter message to send (or type 'quit' to exit): ")
        if message.lower() == 'quit':
            break
        client.send_message(message)

    client.close()

if __name__ == "__main__":
    main()
