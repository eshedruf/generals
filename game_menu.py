import pygame_menu
from pygame_menu.examples import create_example_window
from typing import Tuple, Any
from constants import *

class GameMenu:
    def __init__(self):
        self.surface = create_example_window('Example - Simple', (MENU_WIDTH, MENU_HEIGHT))
        self.menu = pygame_menu.Menu(
            width=MENU_WIDTH,
            height=MENU_HEIGHT,
            theme=pygame_menu.themes.THEME_BLUE,
            title='Game Menu',
        )

        # Align IP address and port inputs in the center
        self.name = self.menu.add.text_input('Name (optional): ', maxchar=20, align=pygame_menu.locals.ALIGN_LEFT)
        self.ipaddr = self.menu.add.text_input('IP Address: ', maxchar=15, align=pygame_menu.locals.ALIGN_LEFT)
        self.port = self.menu.add.text_input('Port: ', maxchar=5, align=pygame_menu.locals.ALIGN_LEFT)
        self.menu.add.button('Join', self.start_the_game)
        self.menu.add.button('Quit', pygame_menu.events.EXIT)

    def set_difficulty(self, selected: Tuple, value: Any) -> None:
        """
        Set the difficulty of the game.
        """
        print(f'Set difficulty to {selected[0]} ({value})')

    def start_the_game(self) -> None:
        """
        Function that starts a game. This is raised by the menu button,
        here menu can be disabled, etc.
        """
        print(f'{self.ipaddr.get_value()}:{self.port.get_value()}, Do the job here!')

    def run(self):
        self.menu.mainloop(self.surface)

if __name__ == '__main__':
    game_menu = GameMenu()
    game_menu.run()
