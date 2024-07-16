import blessed
from enum import Enum
import time

from constants.cli_menu import *

class MenuOption(Enum):
    PLAYERS_COUNT = 0
    READY_STATUS = 1

class CLIMenu:
    def __init__(self, server):
        self.term = blessed.Terminal()
        self.connection_count = MIN_COUNT
        self.server = server
        self.ready = False
        self.start = False
        self.selected_option = MenuOption.PLAYERS_COUNT

    def display_settings_menu(self):
        with self.term.fullscreen(), self.term.cbreak():
            print(self.term.hide_cursor)
            while not self.ready:
                self._settings_header()
                self._settings_options()
                self._handle_keypress(self._settings_keypress)

    def _settings_header(self):
        print(self.term.clear)
        print(self.term.move_y(self.term.height // 2 - 1)) 
        print(self.term.center("Settings"))
        print(self.term.move_y(self.term.height // 2))
        print(self.term.center("---------------"))

    def _settings_options(self):
        players_option = f"Players: {self.connection_count} ({MIN_COUNT}-{MAX_COUNT})"
        not_ready_option = "Not Ready" if not self.ready else "Ready"
        options = [players_option, not_ready_option]
        for i, option_text in enumerate(options):
            if i == self.selected_option.value:
                print(self.term.reverse(self.term.center(option_text)))
            else:
                print(self.term.center(option_text))

    def _handle_keypress(self, keypress_handler):
        key = self.term.inkey()
        keypress_handler(key)

    def _settings_keypress(self, key):
        match key.name:
            case 'KEY_UP':
                self.selected_option = MenuOption((self.selected_option.value - 1) % len(MenuOption))
            case 'KEY_DOWN':
                self.selected_option = MenuOption((self.selected_option.value + 1) % len(MenuOption))
            case 'KEY_LEFT' if self.selected_option == MenuOption.PLAYERS_COUNT:
                self.connection_count = max(MIN_COUNT, self.connection_count - 1)
            case 'KEY_RIGHT' if self.selected_option == MenuOption.PLAYERS_COUNT:
                self.connection_count = min(MAX_COUNT, self.connection_count + 1)
            case 'KEY_ENTER' if self.selected_option == MenuOption.READY_STATUS:
                self.ready = True

    def display_waiting_menu(self):
        with self.term.fullscreen(), self.term.cbreak():
            print(self.term.hide_cursor)
            print(self.term.clear)
            print(self.term.move_y(0))
            print(self.term.move_x(2) + "Waiting for connections...")
            print(self.term.move_y(2))
            print(self.term.move_x(2) + self.term.bold_red("IP Address:"), self.server.get_ip())
            print(self.term.move_x(2) + self.term.bold_green(f"Port:"), str(self.server.port))
            while True:
                if self.server.connected_clients == self.server.num_players:
                    return
                print(self.term.move_y(4))  
                print(self.term.move_x(2) + self.term.bold_blue("Connected Clients:"), str(self.server.connected_clients) + "/" + str(self.server.num_players))
                time.sleep(1)
