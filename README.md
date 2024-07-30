# Generals
This game is a fork of the game generals.io, rewritten from scratch in python. The game is
multi-cliented, and the players play against each other in real time.

## Running instructions
1. Create a new python virtual environment inside the directory of the project with:
   ```sh
   python -m venv venv
   
3. Activate the venv with:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Install required modules: \
   `pip install blessed numpy pygame pygame-menu` \
   `pip install -e .`
5. To start a server, run:
   - Windows: `python server\main.py`
   - Linux/Mac: `python server/main.py`
6. To start a client, run:
   - Windows: `python client\main.py`
   - Linux/Mac: `python client/main.py`


## How to play
The map is made up of 25x25 tiles, and there are four types of tiles: king, army, mountain and city.
Each player starts with a single tile of type "king". The king is the most important tile for the player,
because if captured, the player loses. The king also generates 1 new army each turn, which essentially also 
makes it a fast army spawner. The player can use arrow keys or WASD keys to move an amount of army from a 
tile they own to another, for example:
If player 1 has 50 army on a certain tile, and he wants to capture player 2's tile which only has 30 army,
player 1 will capture player 2's tile, with 20 army remained on the captured tile (50-30 = 20).

The tiles of type "army" are regular tiles the player can capture and progress over the map.
The tiles of type "mountain" are tiles which cannot be captured, they are obstacles.
Tiles of type "city" have an initial amount of army before they can be captured, but once captured
they are used as fast army spawner just like the king.

The players need to find and capture other player's kings, and be the last one standing. When a player captures
another player's king, they get all the tiles the defeated player owned, and his king becomes a city.

