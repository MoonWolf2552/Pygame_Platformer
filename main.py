import os
import sqlite3
import sys
import pygame
import pyganim
import pygame_menu
from pathlib import Path
from typing import *
from constants import *

pygame.init()
pygame.display.set_caption('Dark Souls - Prepare To Die Edition')
pygame.display.set_icon(pygame.image.load("data/img/icon.jpg"))
screen = pygame.display.set_mode(SIZE)
all_levels = len(list(Path('data/levels').iterdir()))
clock = pygame.time.Clock()
user_name = 'Unnamed'
level = []
all_coins = 0


def sound_load(sound_path: str = 'data/sounds') -> dict:
    """Загружает словарь звуков"""
    sound_files = [f for f in os.listdir(sound_path) if os.path.isfile(os.path.join(sound_path, f))]
    return {file_name.split('.')[0]: pygame.mixer.Sound(os.path.join(sound_path, file_name)) for
            file_name in
            sound_files}


# чтоб не мучатся с пробросом звуков делаем глобально
sounds = sound_load()


def loadLevel(levelnum: str) -> list:
    """
    Загрузка уровня
    """
    global playerX, playerY, all_coins  # объявляем глобальные переменные, это координаты героя

    levelFile = open(f'data/levels/{levelnum}')
    line = " "
    level = []
    all_coins = 0
    while line[0] != "/":  # пока не нашли символ завершения файла
        line = levelFile.readline()  # считываем построчно
        if line and line[0] == "[":  # если нашли символ начала уровня
            while line[0] != "]":  # то, пока не нашли символ конца уровня
                line = levelFile.readline()  # считываем построчно уровень
                if line[0] != "]":  # и если нет символа конца уровня
                    endLine = line.find("|")  # то ищем символ конца строки
                    level.append(
                        line[0: endLine])  # и добавляем в уровень строку от начала до символа "|"

        if line:  # если строка не пустая
            commands = line.split()  # разбиваем ее на отдельные команды
            if len(commands) > 1:  # если количество команд > 1, то ищем эти команды
                if commands[0] == "player":  # если первая команда - player
                    playerX = int(commands[1]) * CELL_SIZE  # то записываем координаты героя
                    playerY = int(commands[2]) * CELL_SIZE

                if commands[0] == "portal":  # если первая команда portal, то создаем портал
                    tp = BLockTeleport(int(commands[1]) * CELL_SIZE, int(commands[2]) * CELL_SIZE,
                                       int(commands[3]) * CELL_SIZE, int(commands[4]) * CELL_SIZE)
                    platforms.append(tp)
                    animatedEntities.add(tp)

                if commands[0][:-1] == "monster":  # если первая команда monster, то создаем монстра
                    anim = ANIMATION_MONSTERH1
                    if commands[0][-1] == '2':
                        anim = ANIMATION_MONSTERH2
                    mn = Monster(int(commands[1]) * CELL_SIZE, int(commands[2]) * CELL_SIZE,
                                 int(commands[3]), int(commands[4]) * CELL_SIZE, anim,
                                 commands[0][-1])
                    entities.add(mn)
                    platforms.append(mn)
                    monsters.add(mn)

                if commands[0] == "flying_monster":  # если первая команда flying_monster, то создаем летающего монстра
                    fl_mn = FlyingMonster(int(commands[1]) * CELL_SIZE,
                                           int(commands[2]) * CELL_SIZE,
                                           int(commands[3]), float(commands[4]),
                                           int(commands[5]) * CELL_SIZE,
                                           int(commands[6]))
                    entities.add(fl_mn)
                    platforms.append(fl_mn)
                    monsters.add(fl_mn)

                if commands[0] == "coin":  # если первая команда portal, то создаем портал
                    c = Coin(int(commands[1]) * CELL_SIZE, int(commands[2]) * CELL_SIZE)
                    all_coins += 1
                    platforms.append(c)
                    animatedEntities.add(c)
    return level


def load_image(name: str, directory: str = 'blocks', colorkey=None) -> pygame.Surface:
    fullname = os.path.join(f'data/{directory}', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Monster(sprite.Sprite):
    """
    Монстр, двигается по горизонтали
    """

    def __init__(self, x: int, y: int, left: int, maxLengthLeft: int, ANIMATION: list,
                 num: str) -> None:
        super().__init__()
        Monster.image = load_image('r1.png', f'monsters/{num}')
        self.image = Monster.image
        self.rect = self.image.get_rect()
        soo = CELL_SIZE / self.rect[3]
        self.image = pygame.transform.scale(Monster.image, (self.rect[2] * soo, self.rect[3] * soo))
        self.rect = self.image.get_rect()
        self.image.set_colorkey(MONSTER_COLOR)
        self.rect.x = x
        self.rect.y = y
        self.startX = x  # начальные координаты
        self.startY = y
        self.maxLengthLeft = maxLengthLeft  # максимальное расстояние, которое может пройти в одну сторону
        self.xvel = left  # cкорость передвижения по горизонтали, 0 - стоит на месте

        animation_speed = 100
        if num == '2':
            animation_speed = 150
        boltAnim = []
        for anim in ANIMATION:
            boltAnim.append((anim, animation_speed))
        self.boltAnimRight = pyganim.PygAnimation(boltAnim)
        if num == '2':
            self.boltAnimRight.scale((self.rect[2] + 8, self.rect[3]))
        else:
            self.boltAnimRight.scale((self.rect[2], self.rect[3]))
        self.boltAnimRight.play()

        self.boltAnimLeft = self.boltAnimRight.getCopy()
        self.boltAnimLeft.flip(True, False)
        self.boltAnimLeft.play()

    def update(self, *args) -> None:  # по принципу героя

        self.image.fill(MONSTER_COLOR)
        if self.xvel > 0:
            self.boltAnimRight.blit(self.image, (0, 0))
        if self.xvel < 0:
            self.boltAnimLeft.blit(self.image, (0, 0))

        self.rect.x += self.xvel

        self.collide(platforms)

        if abs(self.startX - self.rect.x) > self.maxLengthLeft:
            self.xvel = -self.xvel  # если прошли максимальное растояние, то идем в обратную сторону

    def collide(self, platforms: list) -> None:
        for p in platforms:
            if sprite.collide_rect(self, p) and self != p:  # если с чем-то или кем-то столкнулись
                self.xvel = -self.xvel  # то поворачиваем в обратную сторону


class FlyingMonster(sprite.Sprite):
    """
    Монстр, двигается по горизонтали и вертикали
    """
    image = load_image('f2.png', 'monsters/fl')

    def __init__(self, x: int, y: int, left: int, up: float, maxLengthLeft: int,
                 maxLengthUp: int) -> None:
        super().__init__()
        self.image = FlyingMonster.image
        self.rect = self.image.get_rect()
        soo = CELL_SIZE * 1.2 / self.rect[2]
        self.image = pygame.transform.scale(FlyingMonster.image,
                                            (self.rect[2] * soo, self.rect[3] * soo))
        self.rect = self.image.get_rect()
        self.image.set_colorkey(FLYING_MONSTER_COLOR)
        self.rect.x = x
        self.rect.y = y
        self.startX = x  # начальные координаты
        self.startY = y
        self.maxLengthLeft = maxLengthLeft  # максимальное расстояние, которое может пройти в одну сторону
        self.maxLengthUp = maxLengthUp  # максимальное расстояние, которое может пройти в одну сторону, вертикаль
        self.xvel = left  # cкорость передвижения по горизонтали, 0 - стоит на месте
        self.yvel = up  # скорость движения по вертикали, 0 - не двигается

        boltAnim = []
        for anim in ANIMATION_MONSTERVERTICAL:
            boltAnim.append((anim, 100))
        self.boltAnimRight = pyganim.PygAnimation(boltAnim)
        self.boltAnimRight.scale((self.rect[2], self.rect[3]))
        self.boltAnimRight.play()

        self.boltAnimLeft = self.boltAnimRight.getCopy()
        self.boltAnimLeft.flip(True, False)
        self.boltAnimLeft.play()

    def update(self, *args) -> None:  # по принципу героя

        self.image.fill(FLYING_MONSTER_COLOR)
        if self.xvel > 0:
            self.boltAnimRight.blit(self.image, (0, 0))
        if self.xvel < 0:
            self.boltAnimLeft.blit(self.image, (0, 0))

        self.rect.y += self.yvel
        self.rect.x += self.xvel

        self.collide(platforms)

        if abs(self.startX - self.rect.x) > self.maxLengthLeft:
            self.xvel = -self.xvel  # если прошли максимальное растояние, то идеи в обратную сторону
        if abs(self.startY - self.rect.y) > self.maxLengthUp:
            self.yvel = -self.yvel  # если прошли максимальное растояние, то идеи в обратную сторону, вертикаль

    def collide(self, platforms: list) -> None:
        for p in platforms:
            if sprite.collide_rect(self, p) and self != p:  # если с чем-то или кем-то столкнулись
                if p.rect.right > self.rect.centerx > p.rect.x and self.rect.centerx:
                    self.yvel = -self.yvel
                if p.rect.bottom > self.rect.centery > self.rect.y:
                    self.xvel = -self.xvel  # то поворачиваем в обратную сторону


class Boss(sprite.Sprite):
    """
    Босс, не двигается
    """
    image = load_image('1.png', 'boss')

    def __init__(self, x: int, y: int) -> None:
        super().__init__(entities)
        self.image = Boss.image
        self.rect = self.image.get_rect()
        self.image = pygame.transform.scale(Boss.image, (self.rect.width * 5, self.rect.height * 5))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.image.set_colorkey(WHITE)

        boltAnim = []
        for anim in ANIMATION_BOSS:
            boltAnim.append((anim, 300))
        self.boltAnim = pyganim.PygAnimation(boltAnim)
        self.boltAnim.scale((self.rect[2], self.rect[3]))
        self.boltAnim.play()

    def update(self, *args) -> None:
        self.image.fill(WHITE)
        self.boltAnim.blit(self.image, (0, 0))


class BossAttack(sprite.Sprite):
    """
    Атака Босса, движется по горизонтали
    """
    image = load_image('attack.png', 'boss')

    def __init__(self, x: int, y: int) -> None:
        super().__init__(entities)
        self.image = pygame.transform.scale(BossAttack.image, (CELL_SIZE * 2, CELL_SIZE * 5))
        self.image.set_alpha(200)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.width = 0
        self.rect.x = x
        self.rect.y = y
        self.vx = -10

    def update(self, *args) -> None:
        self.rect.x += self.vx
        if self.rect.x < 50:
            boss_attacks.pop(0)
            platforms.pop(platforms.index(self))
            self.kill()


class BLock(sprite.Sprite):
    """
    Обычный блок
    """

    def __init__(self, x: int, y: int, image: pygame.Surface = load_image('block.png')) -> None:
        super().__init__(entities)
        self.image = pygame.transform.scale(image, (CELL_SIZE, CELL_SIZE))
        self.rect = Rect(x, y, CELL_SIZE, CELL_SIZE)


class InvisibleBLock(BLock):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y)
        self.image.set_alpha(0)


class SecretBLock(BLock):
    """
    Блок-секретка, исчезает при соприкосновении
    """

    def __init__(self, x: int, y: int, image: pygame.Surface = load_image('block.png')) -> None:
        super().__init__(x, y, image)
        self.img = pygame.transform.scale(image, (CELL_SIZE, CELL_SIZE))

    def hide(self) -> None:
        self.image.set_alpha(128)

    def show(self) -> None:
        self.image.set_alpha(255)


class BLockDie(BLock):
    """
    Убивающий блок
    """

    def __init__(self, x: int, y: int, image: pygame.Surface) -> None:
        super().__init__(x, y, image)
        self.rect.width = 0
        # self.image = pygame.transform.scale(image, (CELL_SIZE + 5, CELL_SIZE + 5))
        # self.rect = Rect(x, y, CELL_SIZE + 5, CELL_SIZE + 5)
        # self.mask = pygame.mask.from_surface(self.image)


class BLockTeleport(BLock):
    """
    Телепорт
    """

    def __init__(self, x: int, y: int, goX: int, goY: int) -> None:
        super().__init__(x, y)
        self.goX = goX  # координаты назначения перемещения
        self.goY = goY  # координаты назначения перемещения
        self.image.set_colorkey(COLOR)
        boltAnim = []
        for anim in ANIMATION_BLOCKTELEPORT:
            boltAnim.append((anim, 1))
        self.boltAnim = pyganim.PygAnimation(boltAnim)
        self.boltAnim.scale((CELL_SIZE, CELL_SIZE))
        self.boltAnim.play()

    def update(self, *args) -> None:
        self.image.fill(COLOR)
        self.boltAnim.blit(self.image, (0, 0))


class Coin(BLock):
    """
    Монетка
    """

    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y)
        self.image = pygame.transform.scale(load_image('coin.png', 'blocks'), (CELL_SIZE, CELL_SIZE))


class Flag(BLock):
    """
    Конец уровня
    """

    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y)
        self.image = pygame.transform.scale(load_image('bonfire.png', 'flag'), (CELL_SIZE, CELL_SIZE * 1.5))


def finish_level(user_name: str, levelnum: int, coins: int) -> None:
    update_bd(user_name, levelnum, coins)
    result_screen()


class Hero(sprite.Sprite):
    """
    Игровой персонаж
    """
    image = load_image('sr.png', 'hero')

    def __init__(self, x: int, y: int) -> None:
        super().__init__(entities)
        self.image = Hero.image
        self.rect = self.image.get_rect()
        soo = CELL_SIZE / self.rect[3]
        self.image = pygame.transform.scale(Hero.image, (self.rect[2] * soo, self.rect[3] * soo))
        self.rect = self.image.get_rect()
        self.image.set_colorkey(COLOR)
        self.rect.x = x
        self.rect.y = y
        self.start_coords = self.startX, self.startY = x, y
        self.xvel = 0  # скорость горизонтального перемещения
        self.yvel = 0  # скорость вертикального перемещения
        self.onGround = False  # На земле ли я?

        # Анимация движения вправо
        boltAnim = []
        for anim in ANIMATION_RIGHT:
            boltAnim.append((anim, ANIMATION_DELAY))
        self.boltAnimRight = pyganim.PygAnimation(boltAnim)
        self.boltAnimRight.scale((self.rect[2], self.rect[3] + 8))
        self.boltAnimRight.play()

        # Анимация движения влево
        self.boltAnimLeft = self.boltAnimRight.getCopy()
        self.boltAnimLeft.flip(True, False)
        self.boltAnimLeft.play()

        self.boltAnimJumpRight = pyganim.PygAnimation(ANIMATION_JUMP_RIGHT)
        self.boltAnimJumpRight.scale((self.rect[2], self.rect[3] + 8))
        self.boltAnimJumpRight.play()

        self.boltAnimJumpLeft = self.boltAnimJumpRight.getCopy()
        self.boltAnimJumpLeft.flip(True, False)
        self.boltAnimJumpLeft.play()

        self.boltAnimStayRight = pyganim.PygAnimation(ANIMATION_STAY_RIGHT)
        self.boltAnimStayRight.scale((self.rect[2], self.rect[3] + 8))
        self.boltAnimStayRight.play()
        self.boltAnimStayRight.blit(self.image, (0, 0))  # По-умолчанию, стоим

        self.boltAnimStayLeft = self.boltAnimStayRight.getCopy()
        self.boltAnimStayLeft.flip(True, False)
        self.boltAnimStayLeft.play()

        self.boltAnimJumpStayRight = pyganim.PygAnimation(ANIMATION_JUMP_STAY_RIGHT)
        self.boltAnimJumpStayRight.scale((self.rect[2], self.rect[3] + 8))
        self.boltAnimJumpStayRight.play()

        self.boltAnimJumpStayLeft = self.boltAnimJumpStayRight.getCopy()
        self.boltAnimJumpStayLeft.flip(True, False)
        self.boltAnimJumpStayLeft.play()

    def update(self, LEVEL_WIDTH: int, LEVEL_HEIGHT: int, left: bool, right: bool, up: bool,
               platforms: list,
               stay_right: bool, *args) -> None:
        if self.rect.y < 0 or self.rect.y > LEVEL_HEIGHT * CELL_SIZE \
                or self.rect.x < 0 or self.rect.x > LEVEL_WIDTH * CELL_SIZE:
            self.die()
            self.yvel = 0

        if up:
            if self.onGround:  # прыгаем, только когда можем оттолкнуться от земли
                self.yvel = -JUMP_POWER
                sounds['jump'].play()
            self.image.fill(COLOR)
            if stay_right:
                self.boltAnimJumpStayRight.blit(self.image, (0, 0))
            else:
                self.boltAnimJumpStayLeft.blit(self.image, (0, 0))

        if left:
            self.xvel = -MOVE_SPEED  # Лево = x- n
            self.image.fill(COLOR)
            if self.yvel < 0:  # для прыжка влево есть отдельная анимация
                self.boltAnimJumpLeft.blit(self.image, (0, 0))
            else:
                self.boltAnimLeft.blit(self.image, (0, 0))

        if right:
            self.xvel = MOVE_SPEED  # Право = x + n
            self.image.fill(COLOR)
            if self.yvel < 0:  # для прыжка вправо есть отдельная анимация
                self.boltAnimJumpRight.blit(self.image, (0, 0))
            else:
                self.boltAnimRight.blit(self.image, (0, 0))

        if not (left or right):  # стоим, когда нет указаний идти
            self.xvel = 0
            if not up:
                self.image.fill(COLOR)
                if stay_right:
                    self.boltAnimStayRight.blit(self.image, (0, 0))
                else:
                    self.boltAnimStayLeft.blit(self.image, (0, 0))

        if not self.onGround:
            self.yvel += GRAVITY

        self.onGround = False  # Мы не знаем, когда мы на земле((
        self.rect.y += self.yvel
        self.collide(0, self.yvel)

        self.rect.x += self.xvel  # переносим свои положение на xvel
        self.collide(self.xvel, 0)

    def collide(self, xvel: int, yvel: float) -> None:
        global coins
        for p in platforms:
            if (isinstance(p, Boss) or isinstance(p, BossAttack) or isinstance(p, BLockDie)) \
                    and sprite.collide_mask(self, p):
                self.die()
                continue

            if sprite.collide_rect(self, p):  # если есть пересечение платформы с игроком
                if isinstance(p, InvisibleBLock):
                    continue

                if isinstance(p, Flag):  # если пересакаемый блок - Flag
                    finish_level(user_name, level_num, coins)  # конец уровня
                    continue

                if isinstance(p, SecretBLock):  # если пересакаемый блок - SecretBLock
                    p.hide()  # блок прячется
                    continue

                if isinstance(p, Coin):  # если пересакаемый блок - Coin
                    sounds['coin'].play()
                    platforms.pop(platforms.index(p))
                    p.kill()
                    coins += 1
                    continue

                if isinstance(p, Monster) or isinstance(p, FlyingMonster):
                    # если пересакаемый блок- Monster или FlyingMonster
                    if self.rect.bottom - 10 <= p.rect.top:
                        if isinstance(p, Monster):
                            sounds['death'].play()
                        elif isinstance(p, FlyingMonster):
                            sounds['flying_monster_dying'].play()
                        platforms.pop(platforms.index(p))
                        p.kill()
                        continue
                    else:
                        self.die()

                if xvel > 0:  # если движется вправо
                    self.rect.right = p.rect.left  # то не движется вправо

                if xvel < 0:  # если движется влево
                    self.rect.left = p.rect.right  # то не движется влево

                if yvel > 0:  # если падает вниз
                    self.rect.bottom = p.rect.top  # то не падает вниз
                    self.onGround = True  # и становится на что1то твердое
                    self.yvel = 0  # и энергия падения пропадает

                if yvel < 0:  # если движется вверх
                    self.rect.top = p.rect.bottom  # то не движется вверх
                    self.yvel = 0  # и энергия прыжка пропадает

                if isinstance(p, Monster):  # если пересакаемый блок- Monster
                    if self.rect.bottom == p.rect.top:
                        platforms.pop(platforms.index(p))
                        p.kill()
                        continue
                    else:
                        self.die()

                # if isinstance(p, BLockDie):
                #     self.die()

                if isinstance(p, BLockTeleport):
                    self.teleporting(p.goX, p.goY)

    def die(self) -> None:
        sounds['you_died'].play()
        death_screen()

    def teleporting(self, goX: int, goY: int) -> None:
        self.rect.x = goX
        self.rect.y = goY


# MENU

def change_name(value: str) -> None:
    """
    Меняем глобальное имя пользователя, опять же чтоб не мучаться с пробром имени между меню и игрой.
    """
    global user_name
    user_name = value


def set_sound_volume(value: Any, volume: float) -> None:
    """
    PyGame mixer не поддерживает глобальной громкости для звуков,
    поэтому нужно каждый звук регулировать отдельно.
    Пробегаем по инстансу звуков и выставляем громкость
    """
    for k, v in sounds.items():
        sounds[k].set_volume(volume)


def menu_start() -> None:
    """
    стартовое меню игры
    """

    ABOUT = ['pygame project от ученика Яндекс Лицея',
             'Author: Ilya Terentyev',
             'Email: iliyaklassgg@gmail.com']

    HELP = ['Управление кнопками <A>, <D> и <SPACE>. Пауза клавиша <P>',
            'Рестарт клавиша <R>',
            'Выйти в меню <Esc>']

    # menu ABOUT
    about_theme = pygame_menu.themes.THEME_DARK.copy()
    about_theme.widget_margin = (0, 0)
    about_menu = pygame_menu.Menu(
        height=HEIGHT * 0.6,
        theme=about_theme,
        title='About',
        width=WIDTH * 0.6,
        mouse_enabled=True
    )

    for m in ABOUT:
        about_menu.add.label(m, align=pygame_menu.locals.ALIGN_CENTER, font_size=20)
    about_menu.add.vertical_margin(30)
    about_menu.add.button('Return to menu', pygame_menu.events.BACK)

    # menu HELP
    help_theme = pygame_menu.themes.THEME_DARK.copy()
    help_theme.widget_margin = (0, 0)
    help_menu = pygame_menu.Menu(
        height=HEIGHT * 0.9,
        theme=help_theme,
        title='Help',
        width=WIDTH * 0.7,
        mouse_enabled=True
    )
    for m in HELP:
        help_menu.add.label(m, margin=(30, 0), align=pygame_menu.locals.ALIGN_LEFT, font_size=20)
    help_menu.add.vertical_margin(30)
    help_menu.add.button('Return to menu', pygame_menu.events.BACK)

    # menu SCORES
    scores_theme = pygame_menu.themes.THEME_DARK
    scores_theme.widget_margin = (0, 0)
    scores_menu = pygame_menu.Menu(
        height=HEIGHT * 0.9,
        theme=scores_theme,
        title='High scores',
        width=WIDTH * 0.7,
        mouse_enabled=True
    )
    c = 0
    for n, s in get_results():
        if c == 10:
            break
        scores_menu.add.label(f'{n} --------- {s * 100}')
        c += 1
    scores_menu.add.vertical_margin(30)
    scores_menu.add.button('Return to menu', pygame_menu.events.BACK)

    # main MENU
    menu = pygame_menu.Menu(height=HEIGHT,
                            width=WIDTH,
                            title='PLATFORMER',
                            theme=pygame_menu.themes.THEME_DARK,
                            mouse_enabled=True
                            )

    img = os.path.join('data/img', 'logo.png')
    menu.add.image(img, scale=(0.6, 0.6), scale_smooth=True)

    menu.add.button('Play', menu_level)
    menu.add.text_input('Name: ', default=user_name, onchange=change_name)
    menu.add.selector('Volume: ', [(f'{i}%', i / 100) for i in range(0, 101, 10)], default=5,
                      onchange=set_sound_volume)
    menu.add.button('High scores', scores_menu)
    menu.add.button('Help', help_menu)
    menu.add.button('About', about_menu)
    menu.add.button('Quit', pygame_menu.events.EXIT)
    menu.mainloop(screen)


def menu_level() -> None:
    """
    menu Levels/Play
    """
    update_name(user_name)

    level_theme = pygame_menu.themes.THEME_DARK.copy()
    level_theme.widget_margin = (0, 0)
    level_menu = pygame_menu.Menu(height=HEIGHT,
                                  width=WIDTH,
                                  title='LEVELS',
                                  theme=level_theme,
                                  mouse_enabled=True
                                  )

    levels = get_levels(user_name)[0]

    for i in range(1, levels + 1):
        level_menu.add.button(f'Level {i}', level_run, i)
    if get_all_coins(user_name)[0] >= 18:
        level_menu.add.button(f'Boss Level', boss_level)
    level_menu.add.vertical_margin(30)
    level_menu.add.button('Return to menu', menu_start)
    level_menu.mainloop(screen)


def get_levels(user_name: str) -> tuple:
    con = sqlite3.connect('data/results.sqlite')
    cur = con.cursor()

    result = cur.execute(f"""SELECT open_levels FROM results
                        WHERE name = '{user_name}'""").fetchone()

    con.close()

    return result


def get_all_coins(user_name: str) -> tuple:
    con = sqlite3.connect('data/results.sqlite')
    cur = con.cursor()

    result = cur.execute(f"""SELECT all_coins FROM results
                            WHERE name = '{user_name}'""").fetchone()

    con.close()

    return result


def update_name(user_name: str) -> None:
    con = sqlite3.connect('data/results.sqlite')
    cur = con.cursor()

    result = cur.execute(f"""SELECT * FROM results
                            WHERE name = '{user_name}'""").fetchone()
    if not result:
        cur.execute(f"""INSERT INTO
                        results(name, open_levels, all_coins, level1, level2, level3, level4, level5, level6, boss_level)
                        VALUES('{user_name}', 1, 0, 0, 0, 0, 0, 0, 0, 0)""")

    con.commit()
    con.close()


def update_bd(user_name: str, levelnum: int, coins: int) -> None:
    con = sqlite3.connect('data/results.sqlite')
    cur = con.cursor()

    if levelnum == 7:
        cur.execute(f"""UPDATE results
                        SET boss_level = 1
                        WHERE name = '{user_name}'""")

        result = cur.execute(f"""SELECT * FROM results
                                    WHERE name = '{user_name}'""").fetchone()

        cur.execute(f"""UPDATE results
                        SET all_coins = {sum(list(result[4:]))}
                        WHERE name = '{user_name}'""")

        con.commit()
        con.close()

        return

    result = cur.execute(f"""SELECT level{levelnum} FROM results
                                WHERE name = '{user_name}'""").fetchone()

    if result[0] < coins:
        cs = coins
    else:
        cs = result[0]

    cur.execute(f"""UPDATE results
                SET level{levelnum} = {cs}
                WHERE name = '{user_name}'""")

    if get_levels(user_name)[0] == levelnum and levelnum < all_levels - 1:
        ln = levelnum + 1
    else:
        ln = get_levels(user_name)[0]

    cur.execute(f"""UPDATE results
                    SET open_levels = {ln}
                    WHERE name = '{user_name}'""")

    result = cur.execute(f"""SELECT * FROM results
                            WHERE name = '{user_name}'""").fetchone()

    cur.execute(f"""UPDATE results
                SET all_coins = {sum(list(result[4:]))}
                WHERE name = '{user_name}'""")

    con.commit()
    con.close()


def get_results() -> list:
    con = sqlite3.connect('data/results.sqlite')
    cur = con.cursor()

    result = cur.execute(f"""SELECT name, all_coins FROM results""").fetchall()

    result.sort(key=lambda x: x[1], reverse=True)

    con.close()

    return result[:10]


def start_screen() -> None:
    fon = Surface(SIZE)
    fon.fill(BLACK)
    screen.blit(fon, (0, 0))

    img = load_image('logo.png', 'img')
    img_rect = img.get_rect()
    img_rect.x = (WIDTH - img_rect[2]) / 2
    img_rect.top = HEIGHT * 2 / 6 - img_rect[3] / 2
    screen.blit(img, img_rect)

    font = pygame.font.Font(None, 30)
    string_rendered = font.render('Press any button to start', True, pygame.Color('white'))
    intro_rect = string_rendered.get_rect()
    intro_rect.x = (WIDTH - intro_rect[2]) / 2
    intro_rect.top = HEIGHT * 3 / 4 - intro_rect[3] / 2
    screen.blit(string_rendered, intro_rect)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                menu_start()
        clock.tick(FPS)
        pygame.display.flip()
    pygame.quit()


def death_screen() -> None:
    bg = Surface(SIZE)
    bg.fill(BLACK)
    screen.blit(bg, (0, 0))

    img = load_image('you_died.png', 'img')
    img = pygame.transform.scale(img, (300 * 2, 178 * 3))
    img_rect = img.get_rect()
    img_rect.x = (WIDTH - img_rect[2]) / 2
    img_rect.top = HEIGHT * 2 / 6 - img_rect[3] / 2
    screen.blit(img, img_rect)

    font = pygame.font.Font(None, 30)
    string_rendered = font.render('Press <SPACE> to continue', True, pygame.Color('white'))
    intro_rect = string_rendered.get_rect()
    intro_rect.x = (WIDTH - intro_rect[2]) / 2
    intro_rect.top = HEIGHT * 3 / 4 - intro_rect[3] / 2
    screen.blit(string_rendered, intro_rect)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == K_SPACE:
                sounds['you_died'].stop()
                if level_num < 7:
                    level_run(level_num)
                else:
                    boss_level()
        clock.tick(FPS)
        pygame.display.flip()
    pygame.quit()


def result_screen() -> None:
    global level_num

    sounds['victory_achieved'].play()

    bg = Surface(SIZE)
    bg.fill(WHITE)
    screen.blit(bg, (0, 0))

    img = load_image('victory.png', 'img')
    img = pygame.transform.scale(img, (694 * 1.5, 67 * 1.5))
    img_rect = img.get_rect()
    img_rect.x = (WIDTH - img_rect[2]) / 2
    img_rect.top = HEIGHT * 2 / 6 - img_rect[3] / 2
    screen.blit(img, img_rect)

    font = pygame.font.Font(None, 30)
    string_rendered = font.render(f'Level {level_num}', True, BLACK)
    intro_rect = string_rendered.get_rect()
    intro_rect.x = (WIDTH - intro_rect[2]) / 2
    intro_rect.top = HEIGHT * 0.15 - intro_rect[3] / 2
    screen.blit(string_rendered, intro_rect)

    font = pygame.font.Font(None, 30)
    string_rendered = font.render(f'{coins} / {all_coins}', True, GOLD)
    intro_rect = string_rendered.get_rect()
    intro_rect.x = (WIDTH - intro_rect[2]) / 2
    intro_rect.top = HEIGHT * 1 / 2 - intro_rect[3] / 2
    screen.blit(string_rendered, intro_rect)

    font = pygame.font.Font(None, 30)
    string_rendered = font.render('Press <SPACE> to continue', True, BLACK)
    intro_rect = string_rendered.get_rect()
    intro_rect.x = (WIDTH - intro_rect[2]) / 2
    intro_rect.top = HEIGHT * 0.8 - intro_rect[3] / 2
    screen.blit(string_rendered, intro_rect)

    font = pygame.font.Font(None, 30)
    string_rendered = font.render('Press <M> to menu', True, BLACK)
    intro_rect = string_rendered.get_rect()
    intro_rect.x = (WIDTH - intro_rect[2]) / 2
    intro_rect.top = HEIGHT * 0.9 - intro_rect[3] / 2
    screen.blit(string_rendered, intro_rect)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == K_SPACE:
                if level_num < 6:
                    sounds['victory_achieved'].stop()
                    level_num += 1
                    level_run(level_num)
            if event.type == pygame.KEYDOWN and event.key == K_m:
                sounds['victory_achieved'].stop()
                menu_level()
        clock.tick(FPS)
        pygame.display.flip()
    pygame.quit()


class Camera(object):
    """
    Камера
    """

    def __init__(self, camera_func: Any, width: float, height: float) -> None:
        self.camera_func = camera_func
        self.state = Rect(0, 0, width, height)

    def apply(self, target: pygame.sprite.Sprite) -> None:
        return target.rect.move(self.state.topleft)

    def update(self, target: pygame.sprite.Sprite) -> None:
        self.state = self.camera_func(self.state, target.rect)


def camera_configure(camera: pygame.Rect, target_rect: pygame.Rect) -> pygame.Rect:
    lf, t, _, _ = target_rect
    _, _, w, h = camera
    lf, t = -lf + WIDTH / 2, -t + HEIGHT / 2

    lf = min(0, lf)  # Не движемся дальше левой границы
    lf = max(-(camera.width - WIDTH), lf)  # Не движемся дальше правой границы
    t = max(-(camera.height - HEIGHT), t)  # Не движемся дальше нижней границы
    t = min(0, t)  # Не движемся дальше верхней границы

    return Rect(lf, t, w, h)


def coin_timer(coins: int, timer: int, levelnum: int, c: Coin) -> None:
    font = pygame.font.Font(None, 60)
    coins = font.render(f'{coins}/{all_coins}', True, GOLD)

    time = font.render(f'{timer // 60:02}:{timer % 60:02}', True, WHITE)

    level = font.render(f'Level {levelnum}', True, WHITE)
    level_rect = level.get_rect()

    rect = Surface((level_rect.width + 2, level_rect.height * 3))
    rect.fill(BLACK)
    screen.blit(rect, (0, 0))
    screen.blit(level, (0, 0))
    screen.blit(c.image, (-5, 25))
    screen.blit(coins, (50, 42))
    screen.blit(time, (0, 85))


def boss_timer(seconds: int) -> None:
    font = pygame.font.Font(None, 60)
    time = font.render('10:59', True, WHITE)
    time_rect = time.get_rect()
    time = font.render(f'{seconds // 60:02}:{seconds % 60:02}', True, WHITE)

    rect = Surface((time_rect.width + 2, time_rect.height + 7))
    rect.fill(BLACK)
    screen.blit(rect, (0, 0))
    screen.blit(time, (0, 7))


entities = pygame.sprite.Group()  # Все объекты
animatedEntities = pygame.sprite.Group()  # все анимированные объекты, за исключением героя
monsters = pygame.sprite.Group()  # Все передвигающиеся объекты
platforms = []  # то, во что мы будем врезаться или опираться
boss_attacks = []  # атаки босса


def level_run(levelnum: int) -> None:
    global level, level_num, coins, entities, animatedEntities, monsters, platforms, JUMP_POWER

    pygame.mouse.set_visible(False)

    entities = pygame.sprite.Group()  # Все объекты
    animatedEntities = pygame.sprite.Group()  # все анимированные объекты, за исключением героя
    monsters = pygame.sprite.Group()  # Все передвигающиеся объекты
    platforms = []  # то, во что мы будем врезаться или опираться

    bg = pygame.transform.scale(load_image('bg.png', ''), SIZE)

    coins = 0

    level = loadLevel(f'{levelnum}.txt')
    level_num = levelnum

    LEVEL_SIZE = LEVEL_WIDTH, LEVEL_HEIGHT = len(level[0]), len(level)

    JUMP_POWER = 11

    for y in range(LEVEL_HEIGHT):
        for x in range(LEVEL_WIDTH):
            coord_x = x * CELL_SIZE
            coord_y = y * CELL_SIZE
            if level[y][x] == "-":
                image = load_image("block.png")
                pt = BLock(coord_x, coord_y, image)
                platforms.append(pt)
            if level[y][x] == "_":
                pt = InvisibleBLock(coord_x, coord_y)
                platforms.append(pt)
            if level[y][x] == ".":
                image = load_image("block.png")
                pt = SecretBLock(coord_x, coord_y, image)
                platforms.append(pt)
            if level[y][x] == "*":
                image = load_image("block_die.png")
                pt = BLockDie(coord_x, coord_y, image)
                platforms.append(pt)
            if level[y][x] == "T":
                image = load_image("block_die.png")
                image = pygame.transform.flip(image, False, True)
                pt = BLockDie(coord_x, coord_y, image)
                platforms.append(pt)
            if level[y][x] == "F":
                pt = Flag(coord_x, coord_y)
                platforms.append(pt)

    hero = Hero(playerX, playerY)

    total_level_width = LEVEL_WIDTH * CELL_SIZE  # Высчитываем фактическую ширину уровня
    total_level_height = LEVEL_HEIGHT * CELL_SIZE  # высоту

    camera = Camera(camera_configure, total_level_width, total_level_height)
    c = Coin(hero.rect.x + 100, hero.rect.y - 100)

    pygame.time.set_timer(pygame.USEREVENT, 1000)
    timer = 120

    start = True
    stay_right = True
    left = right = up = False
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()

            if event.type == pygame.USEREVENT:
                timer -= 1
                if timer <= 0:
                    hero.die()

            if event.type == KEYDOWN and event.key == K_p:
                start = not start

            if event.type == KEYDOWN and event.key == K_r:
                level_run(level_num)

            if event.type == KEYDOWN and event.key == K_ESCAPE:
                menu_start()

            if event.type == KEYDOWN and event.key == K_a:
                left = True
                stay_right = False
            if event.type == KEYDOWN and event.key == K_d:
                right = True
                stay_right = True

            if event.type == KEYUP and event.key == K_d:
                right = False
            if event.type == KEYUP and event.key == K_a:
                left = False

            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_w):
                up = True
            if event.type == KEYUP and (event.key == K_SPACE or event.key == K_w):
                up = False

        tick = clock.tick(FPS)
        if start:
            screen.blit(bg, (0, 0))
            entities.update(LEVEL_WIDTH, LEVEL_HEIGHT, left, right, up, platforms, stay_right)
            animatedEntities.update()
            monsters.update(platforms)  # передвигаем всех монстров
            camera.update(hero)
            c.rect.topleft = camera.state.topleft
            for e in entities:
                screen.blit(e.image, camera.apply(e))
            coin_timer(coins, timer, levelnum, c)
        else:
            font = pygame.font.Font(None, 30)
            string_rendered = font.render('Press <P> to continue', True, pygame.Color('white'))
            intro_rect = string_rendered.get_rect()
            intro_rect.x = (WIDTH - intro_rect[2]) / 2
            intro_rect.top = HEIGHT * 3 / 4 - intro_rect[3] / 2
            screen.blit(string_rendered, intro_rect)
        pygame.display.flip()
    pygame.quit()


def boss_level() -> None:
    global level, level_num, coins, entities, animatedEntities, \
        monsters, platforms, JUMP_POWER, boss_attacks

    pygame.mouse.set_visible(False)

    entities = pygame.sprite.Group()  # Все объекты
    animatedEntities = pygame.sprite.Group()  # все анимированные объекты, за исключением героя
    monsters = pygame.sprite.Group()  # Все передвигающиеся объекты
    platforms = []  # то, во что мы будем врезаться или опираться
    boss_attacks = []  # атаки босса

    bg = pygame.transform.scale(load_image('boss_bg.png', ''), SIZE)

    coins = 0

    level = loadLevel('boss_level.txt')

    level_num = 7
    LEVEL_SIZE = LEVEL_WIDTH, LEVEL_HEIGHT = len(level[0]), len(level)

    JUMP_POWER = 13

    for y in range(LEVEL_HEIGHT):
        for x in range(LEVEL_WIDTH):
            coord_x = x * CELL_SIZE
            coord_y = y * CELL_SIZE
            if level[y][x] == "-":
                image = load_image("block.png")
                pt = BLock(coord_x, coord_y, image)
                platforms.append(pt)
            if level[y][x] == "_":
                pt = InvisibleBLock(coord_x, coord_y)
                platforms.append(pt)

    hero = Hero(playerX, playerY)

    boss = Boss(22 * CELL_SIZE, 9 * CELL_SIZE - 10)
    platforms.append(boss)

    total_level_width = LEVEL_WIDTH * CELL_SIZE  # Высчитываем фактическую ширину уровня
    total_level_height = LEVEL_HEIGHT * CELL_SIZE  # высоту

    camera = Camera(camera_configure, total_level_width, total_level_height)

    pygame.time.set_timer(pygame.USEREVENT, 1000)
    seconds = 120
    num = 2

    start = True
    stay_right = True
    left = right = up = False
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()

            if event.type == pygame.USEREVENT:
                seconds -= 1
                if seconds <= 0:
                    finish_level(user_name, level_num, coins)
                if len(boss_attacks) < num:
                    line = 0
                    if hero.rect.y > CELL_SIZE and hero.rect.y + hero.rect.width < CELL_SIZE * 6:
                        line = 1
                    elif hero.rect.y > CELL_SIZE * 4 and hero.rect.y + hero.rect.width < CELL_SIZE * 9:
                        line = 4
                    elif hero.rect.y > CELL_SIZE * 8 and hero.rect.y + hero.rect.width < CELL_SIZE * 13:
                        line = 8
                    elif hero.rect.y > CELL_SIZE * 10 and hero.rect.y + hero.rect.width < CELL_SIZE * 15:
                        line = 10
                    ba = BossAttack(boss.rect.x, line * CELL_SIZE)
                    boss_attacks.append(ba)
                    platforms.append(ba)

            if event.type == KEYDOWN and event.key == K_p:
                start = not start

            if event.type == KEYDOWN and event.key == K_r:
                level_run(level_num)

            if event.type == KEYDOWN and event.key == K_ESCAPE:
                menu_start()

            if event.type == KEYDOWN and event.key == K_a:
                left = True
                stay_right = False
            if event.type == KEYDOWN and event.key == K_d:
                right = True
                stay_right = True

            if event.type == KEYUP and event.key == K_d:
                right = False
            if event.type == KEYUP and event.key == K_a:
                left = False

            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_w):
                up = True
            if event.type == KEYUP and (event.key == K_SPACE or event.key == K_w):
                up = False

        tick = clock.tick(FPS)
        screen.blit(bg, (0, 0))
        entities.update(LEVEL_WIDTH, LEVEL_HEIGHT, left, right, up, platforms, stay_right)
        camera.update(hero)
        for e in entities:
            screen.blit(e.image, camera.apply(e))
        boss_timer(seconds)
        pygame.display.flip()
    pygame.quit()


if __name__ == '__main__':
    start_screen()
