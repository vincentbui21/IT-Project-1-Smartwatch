# graphics.py
import math
import tkinter as tk

def rgb(r, g, b):
    return f'#{r:02x}{g:02x}{b:02x}'

BLACK = rgb(0, 0, 0)
GREEN = rgb(0, 255, 0)
RED = rgb(255, 0, 0)
LIGHTRED = rgb(140, 0, 0)
BLUE = rgb(0, 0, 255)
YELLOW = rgb(255, 255, 0)
GREY = rgb(100, 100, 100)
LIGHTGREY = rgb(200, 200, 200)
MAGENTA = rgb(255, 0, 255)
CYAN = rgb(0, 255, 255)
LIGHTGREEN = rgb(52, 200, 89)
MEDIUMGREEN = rgb(0, 100, 0)
DARKGREEN = rgb(0, 80, 0)
DARKBLUE = rgb(0, 0, 90)
WHITE = rgb(255, 255, 255)
