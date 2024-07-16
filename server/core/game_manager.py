from enum import Enum, IntEnum
import numpy as np
import random

from constants.colors import *
from shared.map import *

class GameManager:
    def __init__(self, num_players, server):
        self.num_players = num_players
        self.map = Map(num_players)
        self.server = server

        self.map.generate_new()

    


        