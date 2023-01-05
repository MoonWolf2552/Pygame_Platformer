import os
import sqlite3
import sys
import pyganim
import pygame_menu
from pathlib import Path
from typing import *
from constants import *

pygame.init()
pygame.display.set_caption('PyGame')
screen = pygame.display.set_mode(SIZE)
all_levels = len(list(Path('data/levels').iterdir()))
clock = pygame.time.Clock()
user_name = 'Unnamed'


def loadLevel(level_num):
    """
    Загрузка уровня
    """
    global playerX, playerY  # объявляем глобальные переменные, это координаты героя

    levelFile = open(f'%s/data/levels/{level_num}' % FILE_DIR)
    line = " "
    commands = []
    while line[0] != "/":  # пока не нашли символ завершения файла
        line = levelFile.readline()  # считываем построчно
        if line and line[0] == "[":  # если нашли символ начала уровня
            while line[0] != "]":  # то, пока не нашли символ конца уровня
                line = levelFile.readline()  # считываем построчно уровень
                if line[0] != "]":  # и если нет символа конца уровня
                    endLine = line.find("|")  # то ищем символ конца строки
                    level.append(line[0: endLine])  # и добавляем в уровень строку от начала до символа "|"

        if line:  # если строка не пустая
            commands = line.split()  # разбиваем ее на отдельные команды
            if len(commands) > 1:  # если количество команд > 1, то ищем эти команды
                if commands[0] == "player":  # если первая команда - player
                    playerX = int(commands[1]) * CELL_SIZE  # то записываем координаты героя
                    playerY = int(commands[2]) * CELL_SIZE

                if commands[0] == "portal":  # если первая команда portal, то создаем портал
                    tp = BlockTeleport(int(commands[1]) * CELL_SIZE, int(commands[2]) * CELL_SIZE,
                                       int(commands[3]) * CELL_SIZE, int(commands[4]) * CELL_SIZE)
                    platforms.append(tp)
                    animatedEntities.add(tp)

                if commands[0] == "monster":  # если первая команда monster, то создаем монстра
                    mn = Monster(int(commands[1]) * CELL_SIZE, int(commands[2]) * CELL_SIZE,
                                 int(commands[3]), int(commands[4]) * CELL_SIZE)
                    entities.add(mn)
                    platforms.append(mn)
                    monsters.add(mn)

                if commands[0] == "flying_monster":  # если первая команда monster, то создаем монстра
                    fl_mn = Flying_Monster(int(commands[1]) * CELL_SIZE, int(commands[2]) * CELL_SIZE,
                                           int(commands[3]), float(commands[4]), int(commands[5]) * CELL_SIZE,
                                           int(commands[6]))
                    entities.add(fl_mn)
                    platforms.append(fl_mn)
                    monsters.add(fl_mn)

                if commands[0] == "coin":  # если первая команда portal, то создаем портал
                    c = Coin(int(commands[1]) * CELL_SIZE, int(commands[2]) * CELL_SIZE)
                    platforms.append(c)
                    animatedEntities.add(c)


def load_image(name: str, directory='blocks', colorkey=None) -> pygame.Surface:
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
    image = load_image('r1.png', 'monsters')

    def __init__(self, x, y, left, maxLengthLeft):
        """
        Монстр
        """
        super().__init__()
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
        self.xvel = 1  # cкорость передвижения по горизонтали, 0 - стоит на месте

        boltAnim = []
        for anim in ANIMATION_MONSTERHORYSONTAL:
            boltAnim.append((anim, 300))
        self.boltAnimRight = pyganim.PygAnimation(boltAnim)
        self.boltAnimRight.scale((self.rect[2], self.rect[3]))
        self.boltAnimRight.play()

        self.boltAnimLeft = self.boltAnimRight.getCopy()
        self.boltAnimLeft.flip(True, False)
        self.boltAnimLeft.play()

    def update(self, *args):  # по принципу героя

        self.image.fill(Color(MONSTER_COLOR))
        if self.xvel > 0:
            self.boltAnimRight.blit(self.image, (0, 0))
        if self.xvel < 0:
            self.boltAnimLeft.blit(self.image, (0, 0))

        self.rect.x += self.xvel

        self.collide(platforms)

        if abs(self.startX - self.rect.x) > self.maxLengthLeft:
            self.xvel = -self.xvel  # если прошли максимальное растояние, то идем в обратную сторону

    def collide(self, platforms):
        for p in platforms:
            if sprite.collide_rect(self, p) and self != p:  # если с чем-то или кем-то столкнулись
                self.xvel = -self.xvel  # то поворачиваем в обратную сторону


class Flying_Monster(sprite.Sprite):
    image = load_image('r1.png', 'monsters')

    def __init__(self, x, y, left, up, maxLengthLeft, maxLengthUp):
        """
        Летающий монстр
        """
        super().__init__()
        self.image = Flying_Monster.image
        self.rect = self.image.get_rect()
        soo = CELL_SIZE / self.rect[3]
        self.image = pygame.transform.scale(Flying_Monster.image, (self.rect[2] * soo, self.rect[3] * soo))
        self.rect = self.image.get_rect()
        self.image.set_colorkey(MONSTER_COLOR)
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
            boltAnim.append((anim, 300))
        self.boltAnimRight = pyganim.PygAnimation(boltAnim)
        self.boltAnimRight.scale((self.rect[2], self.rect[3]))
        self.boltAnimRight.play()

        self.boltAnimLeft = self.boltAnimRight.getCopy()
        self.boltAnimLeft.flip(True, False)
        self.boltAnimLeft.play()

    def update(self, *args):  # по принципу героя

        self.image.fill(Color(MONSTER_COLOR))
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

    def collide(self, platforms):
        for p in platforms:
            if sprite.collide_rect(self, p) and self != p:  # если с чем-то или кем-то столкнулись
                self.xvel = -self.xvel  # то поворачиваем в обратную сторону
                self.yvel = -self.yvel


class BLock(sprite.Sprite):
    def __init__(self, x, y, image=load_image('block.png')):
        """
        Обычный блок
        """
        super().__init__(entities)
        self.image = pygame.transform.scale(image, (CELL_SIZE, CELL_SIZE))
        self.rect = Rect(x, y, CELL_SIZE, CELL_SIZE)


class Secret_BLock(BLock):
    def __init__(self, x, y, image=load_image('block.png')):
        """
        Блок-секретка
        """
        super().__init__(x, y, image)
        self.img = pygame.transform.scale(image, (CELL_SIZE, CELL_SIZE))

    def hide(self):
        self.image.set_alpha(128)

    def show(self):
        self.image.set_alpha(255)


class BlockDie(BLock):
    def __init__(self, x, y, image):
        """
        Убивающий блок
        """
        super().__init__(x, y, image)


class BlockTeleport(BLock):
    def __init__(self, x, y, goX, goY):
        """
        Телепорт
        """
        super().__init__(x, y)
        self.goX = goX  # координаты назначения перемещения
        self.goY = goY  # координаты назначения перемещения
        boltAnim = []
        for anim in ANIMATION_BLOCKTELEPORT:
            boltAnim.append((anim, 1))
        self.boltAnim = pyganim.PygAnimation(boltAnim)
        self.boltAnim.scale((CELL_SIZE, CELL_SIZE))
        self.boltAnim.play()

    def update(self, *args):
        self.image.fill(COLOR)
        self.boltAnim.blit(self.image, (0, 0))


class Coin(BLock):
    def __init__(self, x, y):
        """
        Монетка
        """
        super().__init__(x + CELL_SIZE / 4, y + CELL_SIZE / 4)
        self.life = True
        boltAnim = []
        for anim in ANIMATION_COIN:
            boltAnim.append((anim, 100))
        self.boltAnim = pyganim.PygAnimation(boltAnim)
        self.boltAnim.scale((CELL_SIZE / 2, CELL_SIZE / 2))
        self.boltAnim.play()

    def update(self, *args):
        self.image.fill(COLOR)
        self.boltAnim.blit(self.image, (0, 0))


class Flag(BLock):
    image = load_image('flag1.png', 'flag')

    def __init__(self, x, y):
        super().__init__(x, y)
        boltAnim = []
        for anim in ANIMATION_FLAG:
            boltAnim.append((anim, 100))
        self.boltAnim = pyganim.PygAnimation(boltAnim)
        self.boltAnim.scale((CELL_SIZE, CELL_SIZE))
        self.boltAnim.play()

    def update(self, *args):
        self.image.fill(COLOR)
        self.boltAnim.blit(self.image, (0, 0))


def finish_level(user_name, level_num, coins):
    update_bd(user_name, level_num, coins)
    menu_start()


class Hero(sprite.Sprite):
    image = load_image('0.png', 'hero')

    def __init__(self, x, y):
        """
        Игровой персонаж
        """
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
        self.boltAnimRight.scale((self.rect[2], self.rect[3]))
        self.boltAnimRight.play()

        # Анимация движения влево
        self.boltAnimLeft = self.boltAnimRight.getCopy()
        self.boltAnimLeft.flip(True, False)
        self.boltAnimLeft.play()

        self.boltAnimStay = pyganim.PygAnimation(ANIMATION_STAY)
        self.boltAnimStay.scale((self.rect[2], self.rect[3]))
        self.boltAnimStay.play()
        self.boltAnimStay.blit(self.image, (0, 0))  # По-умолчанию, стоим

        self.boltAnimJumpRight = pyganim.PygAnimation(ANIMATION_JUMP_RIGHT)
        self.boltAnimJumpRight.scale((self.rect[2], self.rect[3]))
        self.boltAnimJumpRight.play()

        self.boltAnimJumpLeft = self.boltAnimJumpRight.getCopy()
        self.boltAnimJumpLeft.flip(True, False)
        self.boltAnimJumpLeft.play()

        self.boltAnimJump = pyganim.PygAnimation(ANIMATION_JUMP)
        self.boltAnimJump.scale((self.rect[2], self.rect[3]))
        self.boltAnimJump.play()

    def update(self, LEVEL_WIDTH, LEVEL_HEIGHT, left, right, up, platforms, *args):
        if self.rect.y < 0 or self.rect.y > LEVEL_HEIGHT * CELL_SIZE \
                or self.rect.x < 0 or self.rect.x > LEVEL_WIDTH * CELL_SIZE:
            self.teleporting(*self.start_coords)
            self.yvel = 0

        if up:
            if self.onGround:  # прыгаем, только когда можем оттолкнуться от земли
                self.yvel = -JUMP_POWER
            self.image.fill(COLOR)
            self.boltAnimJump.blit(self.image, (0, 0))

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
                self.boltAnimStay.blit(self.image, (0, 0))

        if not self.onGround:
            self.yvel += GRAVITY

        self.onGround = False  # Мы не знаем, когда мы на земле((
        self.rect.y += self.yvel
        self.collide(0, self.yvel)

        self.rect.x += self.xvel  # переносим свои положение на xvel
        self.collide(self.xvel, 0)

    def collide(self, xvel, yvel):
        global coins
        for p in platforms:
            if sprite.collide_rect(self, p):  # если есть пересечение платформы с игроком
                if isinstance(p, Flag):  # если пересакаемый блок - Flag
                    finish_level(user_name, int(level_num), coins)  # конец уровня
                    continue

                if isinstance(p, Secret_BLock):  # если пересакаемый блок - Secret_BLock
                    p.hide()  # блок прячется
                    continue

                if isinstance(p, Coin):  # если пересакаемый блок - Coin
                    platforms.pop(platforms.index(p))
                    p.kill()
                    coins += 1
                    continue

                if isinstance(p, Monster) or isinstance(p, Flying_Monster):
                    # если пересакаемый блок- Monster или Flying_Monster
                    if self.rect.bottom - 4 <= p.rect.top:
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

                if isinstance(p, BlockDie):  # если пересакаемый блок- BlockDie
                    self.die()  # умираем

                elif isinstance(p, BlockTeleport):
                    self.teleporting(p.goX, p.goY)
            else:
                if isinstance(p, Secret_BLock):  # если непересакаемый блок - Secret_BLock
                    p.show()  # блок появляется

    def die(self):
        death_screen()

    def teleporting(self, goX, goY):
        self.rect.x = goX
        self.rect.y = goY


class Camera(object):
    """
    Камера
    """
    def __init__(self, camera_func, width, height):
        self.camera_func = camera_func
        self.state = Rect(0, 0, width, height)

    def apply(self, target):
        return target.rect.move(self.state.topleft)

    def update(self, target):
        self.state = self.camera_func(self.state, target.rect)


def camera_configure(camera, target_rect):
    lf, t, _, _ = target_rect
    _, _, w, h = camera
    lf, t = -lf + WIDTH / 2, -t + HEIGHT / 2

    lf = min(0, lf)  # Не движемся дальше левой границы
    lf = max(-(camera.width - WIDTH), lf)  # Не движемся дальше правой границы
    t = max(-(camera.height - HEIGHT), t)  # Не движемся дальше нижней границы
    t = min(0, t)  # Не движемся дальше верхней границы

    return Rect(lf, t, w, h)


def start_screen():
    fon = Surface(SIZE)
    fon.fill(BLACK)
    screen.blit(fon, (0, 0))
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
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()


# MENU

def change_name(value):
    """
    Меняем глобальное имя пользователя, опять же чтоб не мучаться с пробром имени между меню и игрой.
    """
    global user_name
    user_name = value


def set_sound_volume(value: Any, volume: float) -> None:
    pass


def menu_start(score: int = 0, level: int = 1) -> None:
    """
    стартовое меню игры
    """

    ABOUT = ['pygame project от ученика Яндекс Лицея',
             'Author: Ilya Terentyev',
             'Email: iliyaklassgg@gmail.com']

    HELP = ['Управление кнопками вправо и влево. Пауза клавиша <P>',
            'Рестарт клавиша <R']

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
    menu.add.selector('Volume: ', [(f'{i}%', i / 100) for i in range(0, 101, 10)], default=5, onchange=set_sound_volume)
    menu.add.button('Help', help_menu)
    menu.add.button('About', about_menu)
    menu.add.button('Quit', pygame_menu.events.EXIT)
    menu.mainloop(screen)


def menu_level():
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
        level_menu.add.button(f'Level {str(i)}', level_run, str(i))
    level_menu.add.vertical_margin(30)
    level_menu.add.button('Return to menu', menu_start)
    level_menu.mainloop(screen)


def get_levels(user_name):
    con = sqlite3.connect('data/results.sqlite')
    cur = con.cursor()

    result = cur.execute(f"""SELECT open_levels FROM results
                        WHERE name = '{user_name}'""").fetchone()

    con.close()

    return result


def update_name(user_name):
    con = sqlite3.connect('data/results.sqlite')
    cur = con.cursor()

    result = cur.execute(f"""SELECT * FROM results
                            WHERE name = '{user_name}'""").fetchone()
    if not result:
        cur.execute(f"""INSERT INTO
                        results(name, open_levels, all_coins, level1, level2, level3, level4, level5, level6)
                        VALUES('{user_name}', 1, 0, 0, 0, 0, 0, 0, 0)""")

    con.commit()
    con.close()


def update_bd(user_name, level_num, coins):
    con = sqlite3.connect('data/results.sqlite')
    cur = con.cursor()
    ln = 0

    cur.execute(f"""UPDATE results
                SET level{level_num} = {coins}
                WHERE name = '{user_name}'""")

    if get_levels(user_name)[0] == int(level_num) and int(level_num) < all_levels:
        ln = int(level_num) + 1
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


def death_screen():
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
                level_run(level_num)
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()


entities = pygame.sprite.Group()  # Все объекты
animatedEntities = pygame.sprite.Group()  # все анимированные объекты, за исключением героя
monsters = pygame.sprite.Group()  # Все передвигающиеся объекты
platforms = []  # то, во что мы будем врезаться или опираться


def level_run(levelnum):
    global level, level_num, coins, entities, animatedEntities, monsters, platforms

    pygame.mouse.set_visible(False)

    entities = pygame.sprite.Group()  # Все объекты
    animatedEntities = pygame.sprite.Group()  # все анимированные объекты, за исключением героя
    monsters = pygame.sprite.Group()  # Все передвигающиеся объекты
    platforms = []  # то, во что мы будем врезаться или опираться

    bg = Surface(SIZE)
    bg.fill(COLOR)

    coins = 0

    level = []
    level_num = levelnum
    loadLevel(f'{levelnum}.txt')
    LEVEL_SIZE = LEVEL_WIDTH, LEVEL_HEIGHT = len(level[0]), len(level)

    for y in range(LEVEL_HEIGHT):
        for x in range(LEVEL_WIDTH):
            coord_x = x * CELL_SIZE
            coord_y = y * CELL_SIZE
            if level[y][x] == "-":
                image = load_image("block.png")
                pt = BLock(coord_x, coord_y, image)
                platforms.append(pt)
            if level[y][x] == ".":
                image = load_image("block.png")
                pt = Secret_BLock(coord_x, coord_y, image)
                platforms.append(pt)
            if level[y][x] == "*":
                image = load_image("platform.png")
                pt = BlockDie(coord_x, coord_y, image)
                platforms.append(pt)
            if level[y][x] == "F":
                pt = Flag(coord_x, coord_y)
                platforms.append(pt)

    hero = Hero(playerX, playerY)

    total_level_width = LEVEL_WIDTH * CELL_SIZE  # Высчитываем фактическую ширину уровня
    total_level_height = LEVEL_HEIGHT * CELL_SIZE  # высоту

    camera = Camera(camera_configure, total_level_width, total_level_height)

    one = True
    start = True
    left = right = up = False
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == KEYDOWN and event.key == K_p:
                start = not start
                one = True

            if event.type == KEYDOWN and event.key == K_r:
                level_run(level_num)

            if event.type == KEYDOWN and event.key == K_ESCAPE:
                menu_start()

            if event.type == KEYDOWN and event.key == K_a:
                left = True
            if event.type == KEYDOWN and event.key == K_d:
                right = True

            if event.type == KEYUP and event.key == K_d:
                right = False
            if event.type == KEYUP and event.key == K_a:
                left = False

            if event.type == KEYDOWN and event.key == K_SPACE:
                up = True
            if event.type == KEYUP and event.key == K_SPACE:
                up = False

        tick = clock.tick(FPS)
        if start:
            screen.blit(bg, (0, 0))
            entities.update(LEVEL_WIDTH, LEVEL_HEIGHT, left, right, up, platforms)
            animatedEntities.update()
            monsters.update(platforms)  # передвигаем всех монстров
            camera.update(hero)
            for e in entities:
                screen.blit(e.image, camera.apply(e))
        else:
            if one:
                one = False
                font = pygame.font.Font(None, 30)
                string_rendered = font.render('Press <P> to continue', True, pygame.Color('white'))
                intro_rect = string_rendered.get_rect()
                intro_rect.x = (WIDTH - intro_rect[2]) / 2
                intro_rect.top = HEIGHT * 3 / 4 - intro_rect[3] / 2
                screen.blit(string_rendered, intro_rect)
        pygame.display.flip()
    print(coins)
    pygame.quit()


if __name__ == '__main__':
    start_screen()
