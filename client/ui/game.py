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

class Player:
    def __init__(self, start_pos, client):
        self.position = start_pos
        self.tiles = [start_pos]
        self.selected_tile = start_pos
        self.can_move = True
        self.client = client

    def move(self, direction):
        if not self.can_move:
            return

        x, y = self.position
        from_x, from_y = x, y

        if direction == UP and y > 0:
            self.position = (x, y - 1)
            self.client.send_action('U', from_x, from_y)
        elif direction == DOWN and y < ROWS - 1:
            self.position = (x, y + 1)
            self.client.send_action('D', from_x, from_y)
        elif direction == LEFT and x > 0:
            self.position = (x - 1, y)
            self.client.send_action('L', from_x, from_y)
        elif direction == RIGHT and x < COLS - 1:
            self.position = (x + 1, y)
            self.client.send_action('R', from_x, from_y)

        if self.position not in self.tiles:
            self.tiles.append(self.position)
        self.selected_tile = self.position

    def select_tile(self, tile):
        if tile in self.tiles:
            self.selected_tile = tile
            self.position = tile
            self.can_move = True
        else:
            self.selected_tile = None
            self.can_move = False

class Game:
    def __init__(self):
        self.num_players = 1
        self.map = Map(self.num_players)
        self.client = Client('127.0.0.99', 12345, self.map)
        self.player = Player((0, 0), self.client)
        self.clock = pygame.time.Clock()

        self.map.generate_new()

        if self.client.connect():
            print("Connected to server...")
            comm_thread = threading.Thread(target=self.client_communication)
            comm_thread.start()

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

    def draw_player(self):
        for tile in self.player.tiles:
            rect = pygame.Rect(tile[0] * TILE_SIZE, tile[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, BLUE, rect)
        if self.player.selected_tile is not None:
            selected_rect = pygame.Rect(self.player.selected_tile[0] * TILE_SIZE, self.player.selected_tile[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
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

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if self.player.can_move:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.player.move(UP)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.player.move(DOWN)
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.player.move(LEFT)
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.player.move(RIGHT)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                grid_pos = (mouse_pos[0] // TILE_SIZE, mouse_pos[1] // TILE_SIZE)
                self.player.select_tile(grid_pos)

    def run(self):
        while True:
            screen.fill(WHITE)
            self.draw_grid()
            self.draw_player()
            self.draw_armies()
            self.handle_events()
            pygame.display.flip()
            self.clock.tick(FPS)

def main():
    pygame.init()
    game = Game()
    game.run()

if __name__ == "__main__":
    main()

