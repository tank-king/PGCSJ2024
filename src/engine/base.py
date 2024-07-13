import pygame

from src.engine.video import Renderer


class BaseStructure:
    def update(self, events: list[pygame.event.Event], dt):
        pass

    def draw(self, surf: pygame.Surface, offset, scale=1.0, angle=0.0):
        pass

    def render(self, renderer: Renderer, offset, scale=1.0, angle=0.0):
        pass
