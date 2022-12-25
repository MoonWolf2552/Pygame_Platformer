import pyganim
from constants import *
from main import platforms, load_image


class Monster(sprite.Sprite):
    image = load_image('0.png', 'hero')

    def __init__(self, x, y, left, maxLengthLeft):
        super().__init__()
        self.image = Surface((MONSTER_WIDTH, MONSTER_HEIGHT))
        self.image.fill(Color(MONSTER_COLOR))
        self.rect = Rect(x, y, MONSTER_WIDTH, MONSTER_HEIGHT)
        self.image.set_colorkey(Color(MONSTER_COLOR))
        self.startX = x  # начальные координаты
        self.startY = y
        self.maxLengthLeft = maxLengthLeft  # максимальное расстояние, которое может пройти в одну сторону
        self.xvel = left  # cкорость передвижения по горизонтали, 0 - стоит на месте

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
            self.xvel = -self.xvel  # если прошли максимальное растояние, то идеи в обратную сторону

    def collide(self, platforms):
        for p in platforms:
            if sprite.collide_rect(self, p) and self != p:  # если с чем-то или кем-то столкнулись
                self.xvel = - self.xvel  # то поворачиваем в обратную сторону