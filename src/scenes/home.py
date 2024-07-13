import random

import pygame

from src.engine.objects import BaseObject
from src.engine.scene import Scene
from src.engine.utils import get_random
from src.engine.video import Renderer


class SquareObject(BaseObject):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.angle = 0
        self.color = pygame.Color(random.choice(list(pygame.color.THECOLORS.keys())))

    def get_rect(self):
        return pygame.Rect(*self.pos, 100, 100)

    def update(self, events: list[pygame.event.Event], dt):
        self.angle += 0 * dt
        self.angle %= 360

    def render(self, renderer: Renderer, offset, scale=1.0, angle=0.0):
        t = renderer.textures[Renderer.TEXTURES.SQUARE_TEX]
        t.color = self.color
        rect = self.rect
        rect.center = self.pos
        rect.x += offset[0]
        rect.y += offset[1]
        rect = rect.scale_by(scale, scale)
        t.draw(None, rect, self.angle + angle)


class Home(Scene):
    def enter(self):
        d = 200
        self.object_manager.add_multiple(
            SquareObject(get_random(-d, d), get_random(-d, d)) for _ in range(10)
        )

    def update(self, events: list[pygame.event.Event], dt):
        super().update(events, dt)
        # self.camera.set_position([0, 0], 0.1)
        # self.camera.set_rotation(0, 0.1)
        keys = pygame.key.get_pressed()
        speed = 50
        if keys[pygame.K_z]:
            self.camera.increase_zoom(0.01 * dt)
        elif keys[pygame.K_x]:
            self.camera.increase_zoom(-0.01 * dt)

        v = pygame.Vector2()
        if keys[pygame.K_w]:
            v += (0, -speed)
        if keys[pygame.K_a]:
            v += (-speed, 0)
        if keys[pygame.K_s]:
            v += (0, speed)
        if keys[pygame.K_d]:
            v += (speed, 0)

        v *= dt

        self.camera.move(*v)

        if keys[pygame.K_LEFT]:
            self.camera.increase_rotation(-1 * dt)
        if keys[pygame.K_RIGHT]:
            self.camera.increase_rotation(1 * dt)

        # self.camera.increase_rotation(1.0 * dt)

    def draw(self, surf: pygame.Surface, offset, scale=1.0, angle=0.0):
        surf.fill(0)
        super().draw(surf, offset, scale, angle)

    def render(self, renderer: Renderer, offset, scale=1.0, angle=0.0):
        renderer.fill('brown')
        super().render(renderer, offset, scale, angle)
