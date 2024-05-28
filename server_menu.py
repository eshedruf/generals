import blessed
from server import *
from enum import Enum

class MenuOption(Enum):
    PLAYERS_COUNT = 0
    READY_STATUS = 1

class ServerMenu:
    def __init__(self) -> None:
        self.term = blessed.Terminal()
        self.players_count = 2  # initial players count
        self.server = Server()
        self._ready = False  # initially not ready
        self.selected_option = MenuOption.PLAYERS_COUNT  # Initial selected option

    def display_settings_menu(self):
        with self.term.fullscreen(), self.term.cbreak():
            print(self.term.hide_cursor)  # Hide the cursor using ANSI escape code
            while True:
                self._settings_header()
                self._settings_options()
                self.selected_option = self._settings_keypress(self.selected_option)

    def _settings_header(self):
        print(self.term.clear)  # Clear the terminal before redrawing
        print(self.term.move_y(self.term.height // 2 - 1))  # Adjusted for two menu options
        print(self.term.center("Settings"))
        print(self.term.move_y(self.term.height // 2))  # Adjusted for two menu options
        print(self.term.center("---------------"))

    def _settings_options(self):
        # Display menu options
        players_option = f"Players: {self.players_count} (2-8)"
        not_ready_option = "Not Ready" if not self._ready else "Ready"
        options = [players_option, not_ready_option]
        for i, option_text in enumerate(options):
            if i == self.selected_option.value:
                print(self.term.reverse(self.term.center(option_text)))
            else:
                print(self.term.center(option_text))

    def _settings_keypress(self, selected_option):
        key = self.term.inkey()
        if key.name == 'KEY_UP':
            selected_option = MenuOption((selected_option.value - 1) % len(MenuOption))
        elif key.name == 'KEY_DOWN':
            selected_option = MenuOption((selected_option.value + 1) % len(MenuOption))
        elif key.name == 'KEY_LEFT' and selected_option == MenuOption.PLAYERS_COUNT:
            self.players_count = max(2, self.players_count - 1)
        elif key.name == 'KEY_RIGHT' and selected_option == MenuOption.PLAYERS_COUNT:
            self.players_count = min(8, self.players_count + 1)
        elif key.name == 'KEY_ENTER' and selected_option == MenuOption.READY_STATUS and not self._ready:
            self._ready = True
            self.display_waiting_menu()  # Display waiting menu when 'Enter' is pressed on "Not Ready"
        return selected_option

    def display_waiting_menu(self):
        with self.term.fullscreen(), self.term.cbreak():
            print(self.term.hide_cursor)  # Hide the cursor using ANSI escape code
            print(self.term.clear)  # Clear the terminal before redrawing
            print(self.term.move_y(0))  # Adjusted for a higher vertical position
            print(self.term.move_x(1) + "Waiting for connections...")
            print(self.term.move_y(2))  # Adjusted for a higher vertical position
            print(self.term.move_x(1) + self.term.bold_red("IP Address: ") + self.server.get_ip())
            print(self.term.move_x(1) + self.term.bold_green(f"Port: ") + str(self.server.port))
            while True:
                pass  # Keep waiting menu displayed without waiting for key press

m = ServerMenu()
m.display_settings_menu()
