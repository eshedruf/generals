import pygame_menu
from pygame_menu.examples import create_example_window
from typing import Tuple, Any
from constants.game_menu import *

class GameMenu:
    def __init__(self, client):
        self.surface = create_example_window('Example - Simple', (WIDTH, HEIGHT))
        self.menu = pygame_menu.Menu(
            width=WIDTH,
            height=HEIGHT,
            theme=pygame_menu.themes.THEME_BLUE,
            title='Game Menu',
        )
        self.client = client

        # Align IP address and port inputs in the center
        self.name = self.menu.add.text_input('Player name (optional): ', maxchar=NAME_MAXCHAR, align=pygame_menu.locals.ALIGN_LEFT)
        self.ipaddr = self.menu.add.text_input('IP Address: ', maxchar=IP_MAXCHAR, align=pygame_menu.locals.ALIGN_LEFT)
        self.port = self.menu.add.text_input('Port: ', maxchar=PORT_MAXCHAR, align=pygame_menu.locals.ALIGN_LEFT)
        self.menu.add.button('Join', self.start_the_game)
        self.menu.add.button('Quit', pygame_menu.events.EXIT)
        
        # Add a label for error message
        self.error_label = self.menu.add.label('', align=pygame_menu.locals.ALIGN_CENTER, font_color=(255, 0, 0))

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
        ip = self.ipaddr.get_value()
        port = self.port.get_value()

        if ip == '192.168.0.113' and port == '12345':
            print(f'{ip}:{port}, Do the job here!')
            self.error_label.set_title('')
        else:
            self.error_label.set_title('Invalid IP or Port!')

    def run(self):
        self.menu.mainloop(self.surface)

if __name__ == '__main__':
    game_menu = GameMenu()
    game_menu.run()
