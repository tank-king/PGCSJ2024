from src.engine.ui import *
from src.engine.utils import *


class HealthBar(UI):
    def __init__(self, x, y, bars):
        super().__init__(x, y)
        self.img1 = load_image(get_path('images', 'ui', 'healthbar_empty.png'), color_key='black', scale=5)
        self.img2 = load_image(get_path('images', 'ui', 'healthbar_full.png'), color_key='black', scale=5)
        self.heart = load_image(get_path('images', 'ui', 'heart.png'), color_key='black', scale=6)
        self.bars = bars
        self.health = bars

    def update(self, events: list[pygame.event.Event], dt):
        for e in events:
            if e.type == EVENTS.HEALTHBAR_CHANGE:
                self.health += e.amount

    def draw(self, surf: pygame.Surface, offset, scale=1.0, angle=0.0):
        bar_offset = 10
        w = self.img1.get_width() / 2
        surf.blit(self.heart, self.heart.get_rect(center=self.pos))
        h_offset = self.heart.get_width() / 2
        for i in range(self.bars):
            if i < self.health:
                surf.blit(self.img2, self.img2.get_rect(center=[h_offset + self.pos.x + (bar_offset + w) * i, self.pos.y]))
            else:
                surf.blit(self.img1, self.img1.get_rect(center=[h_offset + self.pos.x + (bar_offset + w) * i, self.pos.y]))
