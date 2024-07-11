from enum import Enum
import numpy as np
import random

from constants.colors import *
from constants.map import *

class TileType(Enum):
    KING = 'K'
    ARMY = 'A'
    MOUNTAIN = 'M'
    CITY = 'C'

class Tile:
    def __init__(self, type: TileType, owner, army):
        self.type = type
        self.owner = owner
        self.army = army

class Map:
    def __init__(self, num_players):
        self.num_players = num_players
        self.tiles = [[None for _ in range(COLS)] for _ in range(ROWS)]

    def print_tiles(self):
        for y in range(ROWS):
            for x in range(COLS):
                print(self.tiles[y][x].army, end=' ')

    def generate_new(self):
        self._place_kings()
        self._finish_tiles()

    def interaction(self, from_x, from_y, to_x, to_y):
        if self.tiles[to_y][to_x].army < 2:
            return
        
        if self.tiles[to_y][to_x].army >= self.tiles[from_y][from_x].army:
            self.tiles[to_y][to_x].army = self.tiles[to_y][to_x].army - self.tiles[from_y][from_x].army + 1
            self.tiles[from_y][from_x].army = 1
        else:
            self.tiles[to_y][to_x].army = self.tiles[from_y][from_x].army - self.tiles[to_y][to_x].army - 1
            self.tiles[from_y][from_x].army = 1
            self.tiles[to_y][to_x].owner = self.tiles[from_y][from_x].owner

        if self.tiles[to_y][to_x].army < 1:
            self.tiles[to_y][to_x].army = 1
        if self.tiles[from_y][from_x].army < 1:
            self.tiles[from_y][from_x].army = 1

    def _place_kings(self):
        min_distance = self._calculate_min_distance()
        king_positions = []

        while len(king_positions) < self.num_players:
            x, y = random.randint(0, COLS - 1), random.randint(0, ROWS - 1)
            pos = (x, y)
            
            if all(self._distance(pos, king_pos) > min_distance for king_pos in king_positions):
                king_positions.append(pos)
                self.tiles[y][x] = Tile(TileType.KING, owner=1, army=999)

    def _finish_tiles(self):
        for y in range(ROWS):
            for x in range(COLS):
                num = random.random()
                
                if self.tiles[y][x] is not None:
                    continue

                if num < CITY_CHANCE:
                    self.tiles[y][x] = Tile(TileType.CITY, owner=0, army=1)
                elif num < MOUNTAIN_CHANCE:
                    self.tiles[y][x] = Tile(TileType.MOUNTAIN, owner=0, army=0)
                else:
                    self.tiles[y][x] = Tile(TileType.ARMY, owner=0, army=1)

    def _calculate_min_distance(self):
        base_distance = KING_MULTIPLIER * np.floor(np.sqrt(ROWS**2 + COLS**2))
        scaling_factor = (10 - self.num_players) / 8  # Scaling factor decreases as num_players increases
        return base_distance * scaling_factor

    def _distance(self, pos1, pos2):
        return np.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)
    