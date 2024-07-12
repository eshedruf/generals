import sys
import pygame
import threading
import time
from client.network.client import *
from shared.map import *
from constants.game import *
from constants.colors import *

sys.stdout.flush()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Generals.io-like Game")

class Game:
    def __init__(self):
        self.num_players = 1
        self.map = Map(self.num_players)
        self.client = Client('127.0.0.99', 12345, self.map)
        self.clock = pygame.time.Clock()

        if self.client.connect():
            print("Connected to server...")
            comm_thread = threading.Thread(target=self.client_communication)
            comm_thread.start()
        
        while self.map.tiles[0][0] is None:
            time.sleep(0.05)

        self.selected_tile = None
        for y in range(ROWS):
            for x in range(COLS):
                if self.map.tiles[y][x].owner == 1:
                    self.selected_tile = [x, y]
                    break
            if self.selected_tile is not None:
                break

    def client_communication(self):
        while True:
            msg_thread = threading.Thread(target=self.get_message)
            msg_thread.start()
            msg_thread.join()

    def get_message(self):
        msg_type, content = self.client.protocol.get_message(self.client.client_socket)
        if content and content != "":
            self.client.handle_msg(msg_type, content)

    def print_map(self):
        while True:
            print("Printing map...")
            for y in range(ROWS):
                for x in range(COLS):
                    print(self.map.tiles[y][x].army, end=' ')
                print()  # For better readability in the console

            print("\n\n\n")
            time.sleep(1)
            
    def draw_grid(self):
        for x in range(0, WIDTH, TILE_SIZE):
            for y in range(0, HEIGHT, TILE_SIZE):
                rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(screen, BLACK, rect, 1)

    def draw_tiles(self):
        for y in range(ROWS):
            for x in range(COLS):
                tile = self.map.tiles[y][x]
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if tile.owner == 1:
                    pygame.draw.rect(screen, BLUE, rect)
                if self.selected_tile is not None:
                    selected_rect = pygame.Rect(self.selected_tile[0] * TILE_SIZE, self.selected_tile[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    pygame.draw.rect(screen, GREEN, selected_rect, 2)

    def draw_armies(self):
        font = pygame.font.SysFont(None, 24)
        for y in range(ROWS):
            for x in range(COLS):
                tile = self.map.tiles[y][x]
                if tile is not None:
                    army_text = font.render(str(tile.army), True, BLACK)
                    text_rect = army_text.get_rect(center=(x * TILE_SIZE + TILE_SIZE / 2, y * TILE_SIZE + TILE_SIZE / 2))
                    screen.blit(army_text, text_rect)

    def move(self, direction):
        if self.selected_tile is None:
            return
        
        x = self.selected_tile[0]
        y = self.selected_tile[1]

        if direction == UP and y > 0:
            position = [x, y - 1]
            self.client.send_action(x, y, x, y-1)
        elif direction == DOWN and y < ROWS - 1:
            position = [x, y + 1]
            self.client.send_action(x, y, x, y+1)
        elif direction == LEFT and x > 0:
            position = [x - 1, y]
            self.client.send_action(x, y, x-1, y)
        elif direction == RIGHT and x < COLS - 1:
            position = [x + 1, y]
            self.client.send_action(x, y, x+1, y)

        self.selected_tile = position

    def select_tile(self, tile_pos):
        x, y = tile_pos
        # Check if the clicked tile is within the bounds of the map
        if 0 <= x < COLS and 0 <= y < ROWS:
            if self.map.tiles[y][x].owner == 1:
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
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.move(UP)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.move(DOWN)
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.move(LEFT)
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.move(RIGHT)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                tile_pos = (mouse_pos[0] // TILE_SIZE, mouse_pos[1] // TILE_SIZE) # (x < COLS, y < ROWS)
                self.select_tile(tile_pos)

    def run(self):
        while True:
            self.handle_events()
            screen.fill(WHITE)
            self.draw_grid()
            self.draw_tiles()
            self.draw_armies()
            pygame.display.flip()
            self.clock.tick(FPS)

def main():
    pygame.init()
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
