import os
from pygame import *

SIZE = WIDTH, HEIGHT = 1366, 768
FPS = 60

BLACK = Color('black')
WHITE = Color('white')
GREEN = Color('green')
DARKGREEN = Color('darkgreen')
RED = Color('red')
DARKRED = Color('darkred')
PINK = Color('deeppink3')
GOLD = Color('gold')
colors = {
    0: BLACK,
    1: WHITE,
    2: GREEN,
    3: RED,
    4: PINK
}
COLOR = WHITE
CELL_SIZE = 50
HERO_SIZE = HERO_WIDTH, HERO_HEIGT = CELL_SIZE, CELL_SIZE
MOVE_SPEED = 300 / FPS
JUMP_POWER = 11
GRAVITY = 26.25 / FPS

ANIMATION_DELAY = 100  # скорость смены кадров
ANIMATION_RIGHT = [('data/hero/r1.png'),
                   ('data/hero/r2.png'),
                   ('data/hero/r3.png'),
                   ('data/hero/r4.png'),
                   ('data/hero/r5.png'),
                   ('data/hero/r6.png')]
ANIMATION_JUMP_RIGHT = [('data/hero/jr.png', 1)]
ANIMATION_JUMP_STAY_RIGHT = [('data/hero/jsr.png', 1)]
ANIMATION_STAY_RIGHT = [('data/hero/sr.png', 1)]
HERO_COLOR = Color("#2110FF")

ANIMATION_BLOCKTELEPORT = [('data/blocks/tp.png')]

ANIMATION_COIN = [('data/blocks/coin.png')]

MONSTER_SIZE = MONSTER_WIDTH, MONSTER_HEIGHT = CELL_SIZE, CELL_SIZE
MONSTER_COLOR = Color("#2110FF")
FLYING_MONSTER_COLOR = Color("#2110FF")

ANIMATION_MONSTERH1 = [('data/monsters/1/r1.png'),
                       ('data/monsters/1/r2.png'),
                       ('data/monsters/1/r3.png'),
                       ('data/monsters/1/r4.png'),
                       ('data/monsters/1/r5.png'),
                       ('data/monsters/1/r6.png')]
ANIMATION_MONSTERH2 = [('data/monsters/2/r1.png'),
                       ('data/monsters/2/r2.png'),
                       ('data/monsters/2/r3.png'),
                       ('data/monsters/2/r4.png'),
                       ('data/monsters/2/r5.png'),
                       ('data/monsters/2/r6.png'),
                       ('data/monsters/2/r7.png'),
                       ('data/monsters/2/r8.png')]
ANIMATION_MONSTERVERTICAL = [('data/monsters/fl/f2.png'),
                             ('data/monsters/fl/f3.png'),
                             ('data/monsters/fl/f4.png'),
                             ('data/monsters/fl/f5.png'),
                             ('data/monsters/fl/f6.png'),
                             ('data/monsters/fl/f7.png')]

ANIMATION_FLAG = [('data/flag/bonfire.png')]
ANIMATION_FLAG_COPY = [('data/flag/flag1.png'),
                       ('data/flag/flag2.png'),
                       ('data/flag/flag3.png'),
                       ('data/flag/flag4.png'),
                       ('data/flag/flag5.png')]
ANIMATION_BOSS = [('data/boss/1.png'),
                  ('data/boss/2.png'),
                  ('data/boss/3.png'),
                  ('data/boss/4.png')]
