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
COLOR = BLACK
CELL_SIZE = 50
HERO_SIZE = HERO_WIDTH, HERO_HEIGT = CELL_SIZE, CELL_SIZE
MOVE_SPEED = 320 / FPS
JUMP_POWER = 10
GRAVITY = 26.25 / FPS

ANIMATION_DELAY = 100  # скорость смены кадров
ANIMATION_RIGHT = [('data/hero/r1.png'),
                   ('data/hero/r2.png'),
                   ('data/hero/r3.png'),
                   ('data/hero/r4.png'),
                   ('data/hero/r5.png'),
                   ('data/hero/r6.png')]
ANIMATION_JUMP_RIGHT = [('data/hero/jr.png', 1)]
ANIMATION_JUMP = [('data/hero/j.png', 1)]
ANIMATION_STAY = [('data/hero/0.png', 1)]

ANIMATION_BLOCKTELEPORT = [('data/blocks/tp.png')]

ANIMATION_COIN = [('data/blocks/tp.png')]

MONSTER_SIZE = MONSTER_WIDTH, MONSTER_HEIGHT = CELL_SIZE, CELL_SIZE
MONSTER_COLOR = "#2110FF"
ICON_DIR = os.path.dirname(__file__)  # Полный путь к каталогу с файлами
FILE_DIR = os.path.dirname(__file__)

ANIMATION_MONSTERHORYSONTAL = [('%s/data/monsters/r1.png' % ICON_DIR),
                               ('%s/data/monsters/r2.png' % ICON_DIR)]
ANIMATION_MONSTERVERTICAL = [('%s/data/monsters/r1.png' % ICON_DIR),
                             ('%s/data/monsters/r2.png' % ICON_DIR)]

ANIMATION_FLAG = [('%s/data/flag/flag1.png' % ICON_DIR),
                  ('%s/data/flag/flag2.png' % ICON_DIR),
                  ('%s/data/flag/flag3.png' % ICON_DIR),
                  ('%s/data/flag/flag4.png' % ICON_DIR),
                  ('%s/data/flag/flag5.png' % ICON_DIR)]
