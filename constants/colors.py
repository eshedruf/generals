BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARKER_GRAY = (65, 65, 65)
DARK_GRAY = (128, 128, 128)
MIDDLE_GRAY = (187, 187, 187)
LIGHT_GRAY = (220, 220, 220)

BLUE = (62, 101, 213)
RED = (255, 0, 0)
GREEN = (0, 128, 25)
PURPLE = (128, 0, 125)
YELLOW = (246, 127, 55)
CYAN = (0, 129, 128)
MAROON = (129, 0, 0)
PINK = (240, 44, 226)

PLAYER_COLORS = (BLUE, RED, GREEN, PURPLE, YELLOW, CYAN, MAROON, PINK)

def darken_color(rgb: tuple|list, amount):
    r, g, b = rgb
    return (max(0, r - amount), max(0, g - amount), max(0, b - amount))
