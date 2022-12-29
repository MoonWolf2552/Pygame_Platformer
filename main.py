import os
import sys
import pyganim as pyganim
from constants import *
from monster import *

pygame.init()
pygame.display.set_caption('PyGame')
screen = pygame.display.set_mode(SIZE)
pygame.mouse.set_visible(False)
coins = 0
level = []


def loadLevel():
    """
    Загрузка уровня
    """
    global playerX, playerY, level  # объявляем глобальные переменные, это координаты героя

    levelFile = open('%s/levels/1.txt' % FILE_DIR)
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
                                           int(commands[3]), int(commands[4]), int(commands[5]) * CELL_SIZE,
                                           int(commands[6]))
                    entities.add(fl_mn)
                    platforms.append(fl_mn)
                    monsters.add(fl_mn)

                if commands[0] == "coin":  # если первая команда portal, то создаем портал
                    c = Coin(int(commands[1]) * CELL_SIZE, int(commands[2]) * CELL_SIZE)
                    platforms.append(c)
                    animatedEntities.add(c)


def load_image(name: str, directory='blocks', colorkey=None) -> pygame.Surface:
    fullname = os.path.join(directory, name)
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


class BLock(sprite.Sprite):
    def __init__(self, x, y, image=load_image('block.png')):
        """
        Обычный блок
        """
        super().__init__(entities)
        self.image = Surface((CELL_SIZE, CELL_SIZE))
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
        self.image.fill(WHITE)
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
        self.image.fill(WHITE)
        self.boltAnim.blit(self.image, (0, 0))


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
        self.image.set_colorkey(WHITE)
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

    def update(self, *args):
        if self.rect.y < 0 or self.rect.y > LEVEL_HEIGHT * CELL_SIZE \
                or self.rect.x < 0 or self.rect.x > LEVEL_WIDTH * CELL_SIZE:
            self.teleporting(*self.start_coords)
            self.yvel = 0

        if up:
            if self.onGround:  # прыгаем, только когда можем оттолкнуться от земли
                self.yvel = -JUMP_POWER
            self.image.fill(WHITE)
            self.boltAnimJump.blit(self.image, (0, 0))

        if left:
            self.xvel = -MOVE_SPEED  # Лево = x- n
            self.image.fill(WHITE)
            if up:  # для прыжка влево есть отдельная анимация
                self.boltAnimJumpLeft.blit(self.image, (0, 0))
            else:
                self.boltAnimLeft.blit(self.image, (0, 0))

        if right:
            self.xvel = MOVE_SPEED  # Право = x + n
            self.image.fill(WHITE)
            if up:
                self.boltAnimJumpRight.blit(self.image, (0, 0))
            else:
                self.boltAnimRight.blit(self.image, (0, 0))

        if not (left or right):  # стоим, когда нет указаний идти
            self.xvel = 0
            if not up:
                self.image.fill(WHITE)
                self.boltAnimStay.blit(self.image, (0, 0))

        if not self.onGround:
            self.yvel += GRAVITY

        self.onGround = False  # Мы не знаем, когда мы на земле((
        self.rect.y += self.yvel
        self.collide(0, self.yvel, platforms)

        self.rect.x += self.xvel  # переносим свои положение на xvel
        self.collide(self.xvel, 0, platforms)

    def collide(self, xvel, yvel, platforms):
        global coins
        for p in platforms:
            if sprite.collide_rect(self, p):  # если есть пересечение платформы с игроком
                if isinstance(p, Secret_BLock):  # если пересакаемый блок - Secret_BLock
                    p.hide()  # блок прячется
                    continue

                if isinstance(p, Coin):  # если пересакаемый блок - Coin
                    platforms.pop(platforms.index(p))
                    p.kill()
                    continue

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

                if isinstance(p, BlockDie) or isinstance(p, Monster):  # если пересакаемый блок- BlockDie или Monster
                    self.die()  # умираем

                elif isinstance(p, BlockTeleport):
                    self.teleporting(p.goX, p.goY)
            else:
                if isinstance(p, Secret_BLock):  # если непересакаемый блок - Secret_BLock
                    p.show()  # блок появляется

    def die(self):
        time.wait(500)
        self.teleporting(self.startX, self.startY)  # перемещаемся в начальные координаты

    def teleporting(self, goX, goY):
        self.rect.x = goX
        self.rect.y = goY


class Camera(object):
    def __init__(self, camera_func, width, height):
        self.camera_func = camera_func
        self.state = Rect(0, 0, width, height)

    def apply(self, target):
        return target.rect.move(self.state.topleft)

    def update(self, target):
        self.state = self.camera_func(self.state, target.rect)


def camera_configure(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    l, t = -l + WIDTH / 2, -t + HEIGHT / 2

    l = min(0, l)  # Не движемся дальше левой границы
    l = max(-(camera.width - WIDTH), l)  # Не движемся дальше правой границы
    t = max(-(camera.height - HEIGHT), t)  # Не движемся дальше нижней границы
    t = min(0, t)  # Не движемся дальше верхней границы

    return Rect(l, t, w, h)


entities = pygame.sprite.Group()  # Все объекты
animatedEntities = pygame.sprite.Group()  # все анимированные объекты, за исключением героя
monsters = pygame.sprite.Group()  # Все передвигающиеся объекты
platforms = []  # то, во что мы будем врезаться или опираться
if __name__ == '__main__':
    clock = pygame.time.Clock()

    bg = Surface(SIZE)
    bg.fill(WHITE)

    loadLevel()
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

    hero = Hero(playerX, playerY)

    total_level_width = LEVEL_WIDTH * CELL_SIZE  # Высчитываем фактическую ширину уровня
    total_level_height = LEVEL_HEIGHT * CELL_SIZE  # высоту

    camera = Camera(camera_configure, total_level_width, total_level_height)

    left = right = up = False
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

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
        screen.blit(bg, (0, 0))
        entities.update(left, right, up, platforms)
        animatedEntities.update()
        monsters.update(platforms)  # передвигаем всех монстров
        camera.update(hero)
        for e in entities:
            screen.blit(e.image, camera.apply(e))
        pygame.display.flip()
    print(coins)
    pygame.quit()
