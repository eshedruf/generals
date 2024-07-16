from network.client import *
from shared.map import Map
from ui.game_menu import *

def main():
    client = Client(None, None, None)
    menu = GameMenu(client)
    while client.
    map = Map()
    client = Client('127.0.0.99', 12345, map)
    client.start()

if __name__ == '__main__':
    main()
