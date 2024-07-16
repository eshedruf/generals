from enum import Enum

from constants.protocol import *
from constants.map import ROWS, COLS, TILE_TYPES
from shared.map import *

class Protocol:
    @staticmethod
    def get_message(s):
        try:
            lenoflen = s.recv(LENOFLEN)
            length = s.recv(int(lenoflen))
            msg = s.recv(int(length))
            msg = msg.decode('utf-8')

            lines = msg.split(SEP)
            msg_type = lines[0]
            lines = lines[1:]
            content = {}

            for line in lines:
                key, value = line.split(":")
                content[key] = value

            return msg_type, content

        except Exception as e:
            print(f"Error in get_message: {e}")
            return ""
    
    @staticmethod
    def handle_msg(msg_type: str, content: dict, map, idlist=None, clients=None, s=None):
        msg_type = msg_type.upper()
        if msg_type == 'M':
            idlist.append(int(content['id'])) # use later, probably for colors in game.py
            tiles = content['tiles']

            tiles = tiles.split('&')

            for tile in tiles:
                x = int(tile[0:2])
                y = int(tile[2:4])
                army = int(tile[4:9])
                owner = int(tile[9:10])
                tile_type = tile[10:11]

                if tile_type not in TILE_TYPES:
                    raise Exception("type not in tiletypes.")

                if map.tiles[y][x] is None:
                    map.tiles[y][x] = Tile(None, None, None)

                map.tiles[y][x].army = army
                map.tiles[y][x].owner = owner
                map.tiles[y][x].type = tile_type

        elif msg_type == 'P':
            coordinates = content['coordinates']
            coordinates = coordinates.split('&')
            from_x = int(coordinates[0])
            from_y = int(coordinates[1])
            to_x = int(coordinates[2])
            to_y = int(coordinates[3])

            if int(map.tiles[from_y][from_x].owner) == int(clients.index(s)+1):
                map.interaction(from_x, from_y, to_x, to_y, int(clients.index(s)+1))
    
    @staticmethod
    def complete_msg(msg):
        length = str(len(msg))
        lenoflen = str(len(length)).zfill(LENOFLEN)
        return lenoflen + length + msg
    
    def create_color_msg(self):
        ...

    @staticmethod
    def create_map_msg(map, id):
        msg = "M" + SEP
        msg += "id:" + str(id) + SEP
        msg += "tiles:"
        for y in range(ROWS):
            for x in range(COLS):
                tile = map.tiles[y][x]

                if tile.owner == id or Protocol._check_strange_tile(map, x, y, id):
                    msg += Protocol._create_tile_msg(x, y, tile.army, tile.owner, tile.type)
                else:
                    if tile.type == MOUNTAIN or tile.type == CITY:
                        msg += Protocol._create_tile_msg(x, y, 0, 0, 'M')
                    elif tile.type == ARMY or tile.type == KING:
                        msg += Protocol._create_tile_msg(x, y, 1, 0, 'A')

                msg += "&"
        msg = msg[:-1] # remove last & from msg
        msg = Protocol.complete_msg(msg)
        
        return msg
    
    @staticmethod
    def _create_tile_msg(x, y, army, owner, type):
        x = str(x).zfill(2)
        y = str(y).zfill(2)
        army = str(army).zfill(5)
        owner = str(owner)

        msg = x + y + army + owner + type

        return msg

    @staticmethod
    def create_action_msg(from_x, from_y, to_x, to_y):
        if not Protocol._adjacent(from_x, from_y, to_x, to_y):
            return False
        
        from_x = str(from_x).zfill(2)
        from_y = str(from_y).zfill(2)
        to_x = str(to_x).zfill(2)
        to_y = str(to_y).zfill(2)
        msg = "P" + SEP
        msg += "coordinates:" + from_x + '&' + from_y + '&' + to_x + '&' + to_y

        msg = Protocol.complete_msg(msg)

        return msg
    
    @staticmethod
    def _check_strange_tile(map, x, y, id):
        """
        if tile in (x,y) has a strange id that is not the id of the current player nor 0,
        this function will check for this tile if it has any adjacent tiles that their id
        is equal to the current player id (id)
        """
        # Check horizontal and vertical adjacents
        if (0 <= x+1 < COLS and map.tiles[y][x+1].owner == id) or \
        (0 <= x-1 < COLS and map.tiles[y][x-1].owner == id) or \
        (0 <= y+1 < ROWS and map.tiles[y+1][x].owner == id) or \
        (0 <= y-1 < ROWS and map.tiles[y-1][x].owner == id):
            return True

        # Check diagonal adjacents
        if (0 <= x+1 < COLS and 0 <= y+1 < ROWS and map.tiles[y+1][x+1].owner == id) or \
        (0 <= x-1 < COLS and 0 <= y+1 < ROWS and map.tiles[y+1][x-1].owner == id) or \
        (0 <= x+1 < COLS and 0 <= y-1 < ROWS and map.tiles[y-1][x+1].owner == id) or \
        (0 <= x-1 < COLS and 0 <= y-1 < ROWS and map.tiles[y-1][x-1].owner == id):
            return True

        return False

    @staticmethod
    def _adjacent(from_x, from_y, to_x, to_y):
        if (from_x < 0 or from_x >= COLS or
            from_y < 0 or from_y >= ROWS or
            to_x < 0 or to_x >= COLS or
            to_y < 0 or to_y >= ROWS):
            return False
        
        # Check edge adjacency (not diagonal)
        if (from_x == to_x and abs(from_y - to_y) == 1) or \
        (from_y == to_y and abs(from_x - to_x) == 1):
            return True
        else:
            return False

if __name__ == '__main__':
    from shared.map import *

    m = Map()

    m.generate_new(3)
    mapmsg = Protocol.create_map_msg(m, 2)
    act = Protocol.create_action_msg(10, 15, 10, 16)
    print()
    #print(mapmsg.split("\r\n")[1].split(' ')[1].split('&')[:-1])


