import math

from src.engine.objects import BaseObject, AnimationStateObject, TimerObject
from src.engine.utils import *
from src.engine.config import *
from src.engine.video import Renderer, Image
from src.objects.explosion import Explosion, Spark
from src.objects.space_station import *


class Bullet(AnimationStateObject):
    def __init__(self, x, y, angle=0, scale=0.75):
        state_info = {
            'default': range(3)
        }
        super().__init__(get_path('images', 'ships', f'bullet.png'), 3, 1, 3, state_info, scale, 1 / 30)
        self.pos = x, y
        self.angle = angle
        self.dx = math.cos(math.radians(angle))
        self.dy = math.sin(math.radians(angle))
        # self.run_once('default', self.destroy)
        self.destroy_timer = TimerObject(1, self.destroy, True)

    def on_ready(self):
        self.object_manager.add(self.destroy_timer)

    def destroy(self):
        self.destroy_timer.destroy()
        super().destroy()

    def get_rect(self):
        return super().get_rect().scale_by(2)

    def update(self, events: list[pygame.event.Event], dt):
        super().update(events, dt)
        speed = 5
        dx = self.dx * dt * speed
        dy = self.dy * dt * speed
        self.move(dx, dy)

    def interact(self, objects: list['BaseObject']):
        for i in objects:
            if isinstance(i, SpriteComponent):
                if i.rect.colliderect(self.rect):
                    # i.destroy()
                    i.get_damage(1)
                    self.destroy()
                    self.object_manager.add(
                        Spark(*self.pos, 2)
                    )

    def render(self, renderer: Renderer, offset, scale=1.0, angle=0.0):
        super().render(renderer, offset, scale, angle + 1 * self.angle)
