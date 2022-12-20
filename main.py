import os
import sys
import pyganim as pyganim
from constants import *

pygame.init()
pygame.display.set_caption('PyGame')
screen = pygame.display.set_mode(SIZE)


def load_image(name: str, directory='data', colorkey=None) -> pygame.Surface:
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


class Platform(sprite.Sprite):
    def __init__(self, x, y, image=load_image('block.png')):
        super().__init__(entities)
        self.image = Surface((CELL_SIZE, CELL_SIZE))
        self.image = pygame.transform.scale(image, (CELL_SIZE, CELL_SIZE))
        self.rect = Rect(x, y, CELL_SIZE, CELL_SIZE)


class BlockDie(Platform):
    def __init__(self, x, y, image):
        Platform.__init__(self, x, y, image)


class BlockTeleport(Platform):
    def __init__(self, x, y, goX, goY):
        Platform.__init__(self, x, y)
        self.goX = goX  # координаты назначения перемещения
        self.goY = goY  # координаты назначения перемещения
        boltAnim = []
        for anim in ANIMATION_BLOCKTELEPORT:
            boltAnim.append((anim, 1))
        self.boltAnim = pyganim.PygAnimation(boltAnim)
        self.boltAnim.play()

    def update(self, *args):
        self.image.fill(GREEN)
        self.boltAnim.blit(self.image, (0, 0))


class Hero(sprite.Sprite):
    image = load_image('0.png', 'hero')

    def __init__(self, x, y):
        super().__init__(entities)
        self.start_coords = self.startX, self.startY = x, y
        self.xvel = 0  # скорость горизонтального перемещения
        self.yvel = 0  # скорость вертикального перемещения
        self.onGround = False  # На земле ли я?
        self.image = pygame.transform.scale(Hero.image, HERO_SIZE)
        self.rect = Rect(x, y, *HERO_SIZE)
        self.image.set_colorkey(RED)  # делаем фон прозрачным

        # Анимация движения вправо
        boltAnim = []
        for anim in ANIMATION_RIGHT:
            boltAnim.append((anim, ANIMATION_DELAY))
        self.boltAnimRight = pyganim.PygAnimation(boltAnim)
        self.boltAnimRight.play()

        # Анимация движения влево
        boltAnim = []
        for anim in ANIMATION_LEFT:
            boltAnim.append((anim, ANIMATION_DELAY))
        self.boltAnimLeft = pyganim.PygAnimation(boltAnim)
        self.boltAnimLeft.play()

        self.boltAnimStay = pyganim.PygAnimation(ANIMATION_STAY)
        self.boltAnimStay.play()
        self.boltAnimStay.blit(self.image, (0, 0))  # По-умолчанию, стоим

        self.boltAnimJumpLeft = pyganim.PygAnimation(ANIMATION_JUMP_LEFT)
        self.boltAnimJumpLeft.play()

        self.boltAnimJumpRight = pyganim.PygAnimation(ANIMATION_JUMP_RIGHT)
        self.boltAnimJumpRight.play()

        self.boltAnimJump = pyganim.PygAnimation(ANIMATION_JUMP)
        self.boltAnimJump.play()

    def update(self, *args):
        if up:
            if self.onGround:  # прыгаем, только когда можем оттолкнуться от земли
                self.yvel = -JUMP_POWER
            self.image.fill(RED)
            self.boltAnimJump.blit(self.image, (0, 0))

        if left:
            self.xvel = -MOVE_SPEED  # Лево = x- n
            self.image.fill(RED)
            if up:  # для прыжка влево есть отдельная анимация
                self.boltAnimJumpLeft.blit(self.image, (0, 0))
            else:
                self.boltAnimLeft.blit(self.image, (0, 0))

        if right:
            self.xvel = MOVE_SPEED  # Право = x + n
            self.image.fill(RED)
            if up:
                self.boltAnimJumpRight.blit(self.image, (0, 0))
            else:
                self.boltAnimRight.blit(self.image, (0, 0))

        if not (left or right):  # стоим, когда нет указаний идти
            self.xvel = 0
            if not up:
                self.image.fill(RED)
                self.boltAnimStay.blit(self.image, (0, 0))

        if not self.onGround:
            self.yvel += GRAVITY

        self.onGround = False  # Мы не знаем, когда мы на земле((
        self.rect.y += self.yvel
        self.collide(0, self.yvel, platforms)

        self.rect.x += self.xvel  # переносим свои положение на xvel
        self.collide(self.xvel, 0, platforms)

    def collide(self, xvel, yvel, platforms):
        for p in platforms:
            if sprite.collide_rect(self, p):  # если есть пересечение платформы с игроком
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

                if isinstance(p, BlockDie):  # если пересакаемый блок - blocks.BlockDie
                    self.die()  # умираем

                elif isinstance(p, BlockTeleport):
                    self.teleporting(p.goX, p.goY)

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
animatedEntities = pygame.sprite.Group()  # все анимированные объекты, за исключением героя
if __name__ == '__main__':
    clock = pygame.time.Clock()

    bg = Surface(SIZE)
    bg.fill(WHITE)

    total_level_width = len(level[0]) * CELL_SIZE  # Высчитываем фактическую ширину уровня
    total_level_height = len(level) * CELL_SIZE  # высоту

    camera = Camera(camera_configure, total_level_width, total_level_height)

    tp = BlockTeleport(100, 500, 800, 64)
    entities.add(tp)
    platforms.append(tp)
    animatedEntities.add(tp)

    for y in range(LEVEL_HEIGHT):
        for x in range(LEVEL_WIDTH):
            coord_x = x * CELL_SIZE
            coord_y = y * CELL_SIZE
            if level[y][x] == "@":
                hero = Hero(coord_x, coord_y)
            if level[y][x] == "-":
                image = load_image("block.png")
                pt = Platform(coord_x, coord_y, image)
                platforms.append(pt)
            if level[y][x] == "*":
                image = load_image("platform.png")
                pt = BlockDie(coord_x, coord_y, image)
                platforms.append(pt)

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
        camera.update(hero)
        animatedEntities.update()
        for e in entities:
            screen.blit(e.image, camera.apply(e))
        pygame.display.flip()
    pygame.quit()