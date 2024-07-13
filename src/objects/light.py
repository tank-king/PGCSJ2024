from typing import Optional

import pygame

from src.engine.objects import BaseObject
from src.engine.utils import get_path
from src.engine.video import Renderer, Image


class SpotLight(BaseObject):
    def __init__(self, x, y, scale=1.0, target: Optional[BaseObject] = None):
        super().__init__(x, y)
        self.target = target
        self.glow: Optional[Image] = None
        self.scale = scale

    def on_renderer_ready(self, renderer: Renderer):
        self.glow = renderer.load_image(get_path('images', 'glow', 'radial-glow.png'))
        self.glow.blend_mode = pygame.BLENDMODE_ADD
        self.glow = Image(self.glow, self.glow.get_rect())

    def render_glow(self, renderer: Renderer, offset, scale=1.0, angle=0.0):
        self.glow.render(*(self.pos + offset), angle, self.scale * scale)
