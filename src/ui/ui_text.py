from src.engine.ui import *
from src.engine.utils import *


class UIText(UI):
    def __init__(self, x, y, msg, size, color):
        super().__init__(x, y)
        text_color = color
        outline_color = 'black'
        outline_width = 2
        self.img = text_with_outline(msg, size, text_color, outline_color, outline_width)
        self.alpha = 255

    def update(self, events: list[pygame.event.Event], dt):
        self.move(0, -2 * dt)
        self.alpha -= 5 * dt
        if self.alpha <= 0:
            self.alpha = 0
            self.destroy()
        self.img.set_alpha(self.alpha)

    def draw(self, surf: pygame.Surface, offset, scale=1.0, angle=0.0):
        surf.blit(self.img, self.img.get_rect(center=self.pos))
