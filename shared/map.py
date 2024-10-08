from enum import Enum
import numpy as np
import random

from constants.colors import *
from constants.map import *

class Tile:
    def __init__(self, type, owner, army):
        self.type = type
        self.owner = owner
        self.army = army

class Map:
    def __init__(self):
        self.tiles = [[None for _ in range(COLS)] for _ in range(ROWS)]

    def generate_new(self, num_players):
        self._place_kings(num_players)
        self._finish_tiles()

    def _place_kings(self, num_players):
        min_distance = self._calculate_min_distance(num_players)
        king_positions = []
        current_owner = 1  # Start with owner 1

        while len(king_positions) < num_players:
            x, y = random.randint(0, COLS - 1), random.randint(0, ROWS - 1)
            pos = (x, y)
            
            # Check if the new position meets the minimum distance requirement from all existing kings
            if all(self._distance(pos, king_pos) > min_distance for king_pos in king_positions):
                king_positions.append(pos)
                self.tiles[y][x] = Tile(KING, owner=current_owner, army=1)
                current_owner += 1  # Increment owner for the next king

    def _finish_tiles(self):
        for y in range(ROWS):
            for x in range(COLS):
                num = random.random()
                
                if self.tiles[y][x] is not None:
                    continue
                    
                # currently ignoring cities
                if num < CITY_CHANCE:
                    self.tiles[y][x] = Tile(CITY, owner=0, army=random.randint(38, 45))
                elif num < MOUNTAIN_CHANCE:
                    self.tiles[y][x] = Tile(MOUNTAIN, owner=0, army=0)
                else:
                    self.tiles[y][x] = Tile(ARMY, owner=0, army=1)

    def print_tiles(self):
        for y in range(ROWS):
            print(f"{y}: ".ljust(4), end='')
            for x in range(COLS):
                print(str(self.tiles[y][x].army).ljust(3), end=' ')
            print()        

    def interaction(self, from_x, from_y, to_x, to_y, id):
        from_tile = self.tiles[from_y][from_x]
        to_tile = self.tiles[to_y][to_x]

        #if to_tile.army < 1 or from_tile.owner != id:
        if from_tile.owner != id: # the army thing will be added later
            return
        
        # if interaction is between 2 tiles of the same player
        if from_tile.owner == to_tile.owner:
            to_tile.army += from_tile.army - 1
            from_tile.army = 1
            return
        
        
        # if interaction is between 2 tiles of different players
        if to_tile.army >= from_tile.army: # if from_tile army smaller (cant transfer ownership)
            to_tile.army = to_tile.army - from_tile.army + 1
            from_tile.army = 1
        else: # if from_tile army bigger (can transfer ownership)
            to_tile.army = from_tile.army - to_tile.army
            from_tile.army = 1
            # if captured a king
            if to_tile.type == KING:
                self._convert_all_tiles(to_tile.owner, from_tile.owner)
            else:
                to_tile.owner = from_tile.owner

        if to_tile.army < 1:
            to_tile.army = 1
        if from_tile.army < 1:
            from_tile.army = 1
    
    def _convert_all_tiles(self, from_id, to_id):
        for y in range(ROWS):
            for x in range(COLS):
                tile = self.tiles[y][x]
                if tile.owner == from_id:
                    tile.owner = to_id
                    if tile.type == KING:
                        tile.type = CITY

    def check_near_tile(self, x, y, id):
        """
        if tile in (x,y) has a strange id that is not the id of the current player nor 0,
        this function will check for this tile if it has any adjacent tiles that their id
        is equal to the current player id (id)
        """
        # Check horizontal and vertical adjacents
        if (0 <= x+1 < COLS and self.tiles[y][x+1].owner == id) or \
        (0 <= x-1 < COLS and self.tiles[y][x-1].owner == id) or \
        (0 <= y+1 < ROWS and self.tiles[y+1][x].owner == id) or \
        (0 <= y-1 < ROWS and self.tiles[y-1][x].owner == id):
            return True

        # Check diagonal adjacents
        if (0 <= x+1 < COLS and 0 <= y+1 < ROWS and self.tiles[y+1][x+1].owner == id) or \
        (0 <= x-1 < COLS and 0 <= y+1 < ROWS and self.tiles[y+1][x-1].owner == id) or \
        (0 <= x+1 < COLS and 0 <= y-1 < ROWS and self.tiles[y-1][x+1].owner == id) or \
        (0 <= x-1 < COLS and 0 <= y-1 < ROWS and self.tiles[y-1][x-1].owner == id):
            return True

        return False

    def tile_exists(x, y):
        if y < 0 or y >= ROWS or x < 0 or x >= COLS:
            return False
        return True


    def _calculate_min_distance(self, num_players):
        base_distance = KING_MULTIPLIER * np.floor(np.sqrt(ROWS**2 + COLS**2))
        scaling_factor = (10 - num_players) / 8  # Scaling factor decreases as num_players increases
        return base_distance * scaling_factor / 2 # division by 2 for radius and not diameter

    def _distance(self, pos1, pos2):
        return np.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)
    
