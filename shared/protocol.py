from enum import Enum

from constants.protocol import *

class Protocol:
    def __init__(self):
        pass

    def get_message(self, s):
        try:
            lenoflen = s.recv(LENOFLEN)
            length = s.recv(int(lenoflen))
            msg = s.recv(int(length))
            msg = msg.decode('utf-8')

            msg = msg.split(SEP)
            msg_type = msg[0]
            content = msg[1].split('&')

            return msg_type, content

        except Exception as e:
            print(f"Error in get_message: {e}")
            return ""

    def complete_msg(self, msg):
        length = str(len(msg))
        lenoflen = str(len(length)).zfill(LENOFLEN)
        return lenoflen + length + msg
    
    def create_color_msg(self):
        ...

    def create_map_msg(self, map):
        rows = len(map.tiles)
        cols = len(map.tiles[0])

        msg = "M" + SEP
        for y in range(rows):
            for x in range(cols):
                msg += self._create_tile_msg(x, y, map.tiles[y][x].army, map.tiles[y][x].owner, map.tiles[y][x].type.value)
                msg += "&"
        msg = msg[:-1] # remove last & from msg
        msg = self.complete_msg(msg)
        
        return msg
    
    def create_action_msg(self, direction, from_x, from_y):
        direction = direction.upper()
        if direction != 'U' and direction != 'D' and direction != 'L' and direction != 'R':
            return False
        
        from_x = str(from_x).zfill(2)
        from_y = str(from_y).zfill(2)
        msg = "P" + SEP
        msg += direction + '&' + from_x + '&' + from_y

        msg = self.complete_msg(msg)

        return msg

    def _create_tile_msg(self, x, y, army, owner, type):
        x = str(x).zfill(2)
        y = str(y).zfill(2)
        army = str(army).zfill(5)
        owner = str(owner)

        msg = x + y + army + owner + type

        return msg

if __name__ == '__main__':
    from shared.map import *

    p = Protocol()
    m = Map(8)

    m.generate_new()
    
    mapmsg = p.create_map_msg(m)
    #print(mapmsg.split("\r\n")[1].split(' ')[1].split('&')[:-1])

    act = p.create_action_msg('U', 10, 15)

