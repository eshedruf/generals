import sys
import os
import pygame
import threading
import time
from client.network.client import *
from shared.map import *
from shared.protocol import *
from constants.game import *
from constants.colors import *

sys.stdout.flush()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Generals.io-like Game")

class Game:
    def __init__(self):
        self.map = Map()
        self.client = Client('127.0.0.99', 12345, self.map)
        self.clock = pygame.time.Clock()
        self.id = None

        # Load and scale sprites once
        base_path = os.path.dirname(__file__)
        SCALE_SIZE = 0.85 * TILE_SIZE
        self.sprites = {
            KING: pygame.transform.scale(pygame.image.load(os.path.join(base_path, 'assets', 'crown.png')), (SCALE_SIZE, SCALE_SIZE)),
            CITY: pygame.transform.scale(pygame.image.load(os.path.join(base_path, 'assets', 'city.png')), (SCALE_SIZE, SCALE_SIZE)),
            MOUNTAIN: pygame.transform.scale(pygame.image.load(os.path.join(base_path, 'assets', 'mountain.png')), (SCALE_SIZE, SCALE_SIZE))
        }

        # Calculate offsets for centering sprites
        self.sprite_offset = (TILE_SIZE - SCALE_SIZE) / 2

        # Create font object once
        self.font = pygame.font.SysFont(None, 24)

        if self.client.connect():
            print("Connected to server...")
            comm_thread = threading.Thread(target=self.client_communication)
            comm_thread.start()
        
        while self.map.tiles[0][0] is None:
            time.sleep(0.05)

        print("id:", self.id)

        self.selected_tile = None
        for y in range(ROWS):
            for x in range(COLS):
                if self.map.tiles[y][x].owner == self.id:
                    self.selected_tile = [x, y]
                    break
            if self.selected_tile is not None:
                break

        print("selected tile:", self.selected_tile)

    def client_communication(self):
        while True:
            msg_thread = threading.Thread(target=self.get_message)
            msg_thread.start()
            msg_thread.join()

    def get_message(self):
        msg_type, content = Protocol.get_message(self.client.client_socket)
        if content and content != "":
            idlist = []
            Protocol.handle_msg(msg_type, content, self.map, idlist=idlist)
            self.id = idlist[0]

    def print_map(self):
        while True:
            print("Printing map...")
            for y in range(ROWS):
                for x in range(COLS):
                    print(self.map.tiles[y][x].army, end=' ')
                print()  # For better readability in the console

            print("\n\n\n")
            time.sleep(1)

    def draw_all(self):
        dirty_rects = []

        for y in range(ROWS):
            for x in range(COLS):
                tile = self.map.tiles[y][x]

                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                
                # Draw colors
                if tile.owner > 0:
                    pygame.draw.rect(screen, PLAYER_COLORS[tile.owner - 1], rect)
                elif tile.owner == 0:
                    if tile.type == ARMY:
                        pygame.draw.rect(screen, LIGHT_GRAY, rect)
                    elif tile.type == MOUNTAIN:
                        pygame.draw.rect(screen, MIDDLE_GRAY, rect)
                    elif tile.type == CITY:
                        pygame.draw.rect(screen, DARK_GRAY, rect)
                if self.selected_tile is not None:
                    selected_rect = pygame.Rect(self.selected_tile[0] * TILE_SIZE, self.selected_tile[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    pygame.draw.rect(screen, GREEN, selected_rect, 2)

                # Draw sprites
                sprite = self.sprites.get(tile.type)
                if sprite:
                    sprite_pos = (x * TILE_SIZE + self.sprite_offset, y * TILE_SIZE + self.sprite_offset)
                    screen.blit(sprite, sprite_pos)

                # Draw armies
                if tile.type != MOUNTAIN and not (tile.type == ARMY and tile.owner == 0):
                    army_text = self.font.render(str(tile.army), True, WHITE)
                    text_rect = army_text.get_rect(center=(x * TILE_SIZE + TILE_SIZE / 2, y * TILE_SIZE + TILE_SIZE / 2))
                    screen.blit(army_text, text_rect)

                # Draw grid
                pygame.draw.rect(screen, BLACK, rect, 1)

                dirty_rects.append(rect)

        return dirty_rects

    def move(self, to_x, to_y):
        from_x = self.selected_tile[0]
        from_y = self.selected_tile[1]

        if self.selected_tile is None or not self._check_exist(to_x, to_y) \
        or self.map.tiles[from_y][from_x].type == MOUNTAIN \
        or self.map.tiles[to_y][to_x].type == MOUNTAIN:
            return
        
        self.client.send_action(from_x, from_y, to_x, to_y)
        self.selected_tile = [to_x, to_y]

    def _check_exist(self, x, y):
        return 0 <= x < COLS and 0 <= y < ROWS

    def select_tile(self, tile_pos):
        x, y = tile_pos
        # Check if the clicked tile is within the bounds of the map
        if self._check_exist(x, y):
            if self.map.tiles[y][x].owner == self.id:
                self.selected_tile = tile_pos
                return True
            else:
                self.selected_tile = None  # Ensure to clear selection if not owned by player
                return False
        else:
            self.selected_tile = None  # Ensure to clear selection if out of bounds
            return False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and self.selected_tile is not None:
                x = self.selected_tile[0]
                y = self.selected_tile[1]
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.move(x, y-1)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.move(x, y+1)
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.move(x-1, y)
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.move(x+1, y)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                tile_pos = (mouse_pos[0] // TILE_SIZE, mouse_pos[1] // TILE_SIZE) # (x < COLS, y < ROWS)
                self.select_tile(tile_pos)

    def run(self):
        while True:
            self.handle_events()
            screen.fill(WHITE)
            dirty_rects = self.draw_all()
            pygame.display.update(dirty_rects)
            self.clock.tick(FPS)

def main():
    pygame.init()
    game = Game()
    game.run()

if __name__ == "__main__":
    main()