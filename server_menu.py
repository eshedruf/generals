import blessed
from server import *
from enum import Enum
import time
import threading

class MenuOption(Enum):
    PLAYERS_COUNT = 0
    READY_STATUS = 1

class ServerMenu:
    def __init__(self) -> None:
        self.term = blessed.Terminal()
        self.connection_count = 2
        self.server = Server()
        self._ready = False
        self.selected_option = MenuOption.PLAYERS_COUNT

    def display_settings_menu(self):
        with self.term.fullscreen(), self.term.cbreak():
            print(self.term.hide_cursor)
            while True:
                self._settings_header()
                self._settings_options()
                self.selected_option = self._settings_keypress(self.selected_option)

    def _settings_header(self):
        print(self.term.clear)
        print(self.term.move_y(self.term.height // 2 - 1)) 
        print(self.term.center("Settings"))
        print(self.term.move_y(self.term.height // 2))
        print(self.term.center("---------------"))

    def _settings_options(self):
        # Display menu options
        players_option = f"Players: {self.connection_count} (2-8)"
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
            self.connection_count = max(2, self.connection_count - 1)
        elif key.name == 'KEY_RIGHT' and selected_option == MenuOption.PLAYERS_COUNT:
            self.connection_count = min(8, self.connection_count + 1)
        elif key.name == 'KEY_ENTER' and selected_option == MenuOption.READY_STATUS and not self._ready:
            self._ready = True
            self.display_waiting_menu()
        return selected_option

    def display_waiting_menu(self):
        self.server.max_connections = self.connection_count
        #threading.Thread(self.server.start()).start()  # לאדע לא עובד
        with self.term.fullscreen(), self.term.cbreak():
            print(self.term.hide_cursor)
            print(self.term.clear)
            print(self.term.move_y(0))
            print(self.term.move_x(1) + "Waiting for connections...")
            print(self.term.move_y(2))
            print(self.term.move_x(1) + self.term.bold_red("IP Address:"), self.server.get_ip())
            print(self.term.move_x(1) + self.term.bold_green(f"Port:"), str(self.server.port))
            while True:
                print(self.term.move_y(4))
                print(self.term.move_x(1) + f"Connected Clients: {len(self.server.connected_clients)}")
                time.sleep(1)

def main():
    m = ServerMenu()
    m.display_settings_menu()

if __name__ == "__main__":
    main()
