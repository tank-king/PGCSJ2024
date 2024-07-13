import math

import pygame

from src.engine.objects import BaseObject
from src.engine.utils import *
from src.engine.config import *
from src.engine.video import Renderer, Image, Texture
from src.objects.space_station import SpriteComponent


class Laser(BaseObject):
    def __init__(self, x, y):
        super().__init__(x, y, LAYERS.PLAYER_LAYER - 0.1)
        self.k = 1
        self.rate = 5
        self.length = 0
        self.max_length = 400
        self.tex: Texture | None = None
        self.angle = 0

        self.start = pygame.Vector2(*self.pos)
        self.end = self.start.copy()

    def on_renderer_ready(self, renderer: Renderer):
        self.tex = renderer.load_image(get_path('images', 'ships', 'laser.png'))
        self.tex.blend_mode = pygame.BLENDMODE_BLEND
        self.tex.color = 'red'

    def update(self, events: list[pygame.event.Event], dt):
        self.start = pygame.Vector2(*self.pos)
        self.length += self.k * self.rate * dt
        if self.length >= self.max_length:
            self.length = self.max_length
        dx = math.cos(math.radians(self.angle))
        dy = math.sin(math.radians(self.angle))
        self.end = self.start + pygame.Vector2(dx, dy) * self.length

    def interact(self, objects: list['BaseObject']):
        objects = []
        for i in self.object_manager.get_objects(SpriteComponent):
            try:
                intersects = i.rect.clipline(self.start, self.end)
                if intersects:
                    objects.append([intersects[1]])
            except AttributeError:
                pass

    def render(self, renderer: Renderer, offset, scale=1.0, angle=0.0):
        rect = pygame.Rect(0, 0, self.length * scale, 10 * scale)
        rect.midleft = self.start + offset
        self.tex.draw(None, rect, self.angle + angle, origin=[0, 5 * scale])
