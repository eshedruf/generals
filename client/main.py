from network.client import *
from shared.map import *
from client.ui.game import *
from ui.game_menu import *
import time

def main():
    client = Client(None, None)
    menu = GameMenu(client)
    menu.run()

    game = Game(client)
    game.run()

if __name__ == '__main__':
    main()
