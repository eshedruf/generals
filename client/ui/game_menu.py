import pygame_menu
import pygame
import sys

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
        #self.name = self.menu.add.text_input('Player name (optional): ', maxchar=NAME_MAXCHAR, align=pygame_menu.locals.ALIGN_LEFT)
        self.ipaddr = self.menu.add.text_input('IP Address: ', maxchar=IP_MAXCHAR, align=pygame_menu.locals.ALIGN_LEFT)
        self.port = self.menu.add.text_input('Port: ', maxchar=PORT_MAXCHAR, align=pygame_menu.locals.ALIGN_LEFT, default=12345)
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
        self.client.ip = self.ipaddr.get_value()
        self.client.port = int(self.port.get_value())

        if self.client.connect():
            pygame.quit()

    def run(self):
        try:
            clock = pygame.time.Clock()
            running = True
            while running:
                events = pygame.event.get()
                for event in events:
                    if event.type == pygame.QUIT:
                        running = False

                    # Check if the Enter key was pressed
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        # Check if the entered name is "name"
                        self.start_the_game()

                if not running:
                    break
                self.menu.update(events)
                self.menu.draw(self.surface)
                pygame.display.update()
                clock.tick(30)
            pygame.quit()
        except Exception as e:
            print(e)

