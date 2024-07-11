from ui.cli_menu import CLIMenu
from network.server import Server
from shared.map import Map
import threading
import random

def main():
    map = Map(1)
    server = Server('127.0.0.99', 12345, map, 1)

    server.start()

    """menu = CLIMenu(server)
    menu.display_settings_menu()

    server.max_clients = menu.connection_count

    server_thread = threading.Thread(target=server.start)
    server_thread.start()

    menu.display_waiting_menu()"""

if __name__ == '__main__':
    main()