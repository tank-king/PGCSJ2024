import pygame

from src.engine.objects import BaseObject, ValueAnimator
from src.engine.sounds import SoundManager
from src.engine.video import Renderer, Image
from src.engine.utils import *

from src.objects.bullet import Bullet


class Ship(BaseObject):
    def __init__(self, x, y, ship):
        super().__init__(x, y)
        self.ship_n = ship
        self.scale_value = ValueAnimator(4)
        self.dscale = 0
        self.img: Image | None = None
        self.flip = False

    def on_ready(self):
        self.object_manager.add(self.scale_value)

    def destroy(self):
        self.scale_value.destroy()
        super().destroy()

    @property
    def scale(self):
        return self.scale_value.value

    def on_renderer_ready(self, renderer: Renderer):
        img = renderer.load_image(get_path('images', 'ships', f'ship{self.ship_n}.png'))
        self.img = Image(img, img.get_rect())

    def update(self, events: list[pygame.event.Event], dt):
        pass

    def shoot(self):
        rate = 0.8
        self.scale_value.set(4).lerp(3.8, rate).lerp(4.2, rate).lerp(4, rate)
        offset = pygame.Vector2(12, 4) * self.scale
        k = 1
        if self.flip:
            offset.x *= -1
            k = -1
        self.object_manager.add(
            Bullet(self.x + offset.x, self.y + offset.y, 10 * k)
        )
        SoundManager.play('shoot')

    def render(self, renderer: Renderer, offset, scale=1.0, angle=0.0):
        self.img.render(*(self.pos + offset), angle, self.scale * scale, (self.flip, 0))
