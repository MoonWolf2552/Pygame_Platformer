import os
import pygame
from pygame import *

SIZE = WIDTH, HEIGHT = 1366, 768
FPS = 75

BLACK = Color('black')
WHITE = Color('white')
GREEN = Color('green')
DARKGREEN = Color('darkgreen')
RED = Color('red')
PINK = Color('deeppink3')
colors = {
    0: BLACK,
    1: WHITE,
    2: GREEN,
    3: RED,
    4: PINK
}
blocks = {
    '1': 'block.png',
    '2': 'platform.png'
}
CELL_SIZE = 50
HERO_SIZE = HERO_WIDTH, HERO_HEIGT = CELL_SIZE, CELL_SIZE
MOVE_SPEED = 480 / FPS
JUMP_POWER = 10
GRAVITY = 0.35
level = [
       "----------------------------------",
       "-                                -",
       "-                       --       -",
       "-        *                       -",
       "-                                -",
       "-            --                  -",
       "--                               -",
       "-                                -",
       "-                   ----     --- -",
       "-                                -",
       "--                               -",
       "-            *                   -",
       "-                            --- -",
       "-                                -",
       "-      @                         -",
       "-  *   ---                  *    -",
       "-      ...                       -",
       "-   -------         ----         -",
       "-                                -",
       "-                         -      -",
       "-                            --  -",
       "-           ***    ^             -",
       "-                                -",
       "----------------------------------"]
LEVEL_SIZE = LEVEL_WIDTH, LEVEL_HEIGHT = len(level[0]), len(level)

ANIMATION_DELAY = 100  # скорость смены кадров
ANIMATION_RIGHT = [('hero/r1.png'),
                   ('hero/r2.png'),
                   ('hero/r3.png'),
                   ('hero/r4.png'),
                   ('hero/r5.png'),
                   ('hero/r6.png')]
ANIMATION_JUMP_RIGHT = [('hero/jr.png', 1)]
ANIMATION_JUMP = [('hero/j.png', 1)]
ANIMATION_STAY = [('hero/0.png', 1)]

ANIMATION_BLOCKTELEPORT = [('blocks/tp.png')]

MONSTER_SIZE = MONSTER_WIDTH, MONSTER_HEIGHT = CELL_SIZE, CELL_SIZE
MONSTER_COLOR = "#2110FF"
ICON_DIR = os.path.dirname(__file__)  # Полный путь к каталогу с файлами

ANIMATION_MONSTERHORYSONTAL = [('%s/monsters/r1.png' % ICON_DIR),
                               ('%s/monsters/r2.png' % ICON_DIR)]