from src.engine.ui import *
from src.engine.utils import *


class IceCrystal(UI):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.img = load_image(get_path('images', 'ui', 'ice_crystal.png'), color_key='white', scale=8)
        self.count = 0
        self.target_count = 0

    def update(self, events: list[pygame.event.Event], dt):
        for e in events:
            if e.type == ADD_MONEY:
                self.target_count += e.money
                # for i in range(e.money):
                if e.money:
                    self.object_manager.add(IceCrystalParticle(*e.pos, self))
        self.count = lerp(self.count, self.target_count, 0.1 * dt)

    def draw(self, surf: pygame.Surface, offset, scale=1.0, angle=0.0):
        surf.blit(self.img, r := self.img.get_rect(center=self.pos))
        t = text_with_outline(f'{round(self.count)}', 50, 'white', 'black', 5)
        surf.blit(t, t.get_rect(topright=r.bottomright))


class IceCrystalParticle(UI):
    def __init__(self, x, y, anchor: UI):
        super().__init__(x, y)
        self.anchor = anchor
        self.size = 0
        self.img = load_image(get_path('images', 'ui', 'ice_crystal.png'), color_key='white', scale=8)

    def update(self, events: list[pygame.event.Event], dt):
        self.pos = self.pos.lerp(self.anchor.pos, 0.1 * dt)
        if self.pos.distance_to(self.anchor.pos) <= 1:
            self.destroy()

    def draw(self, surf: pygame.Surface, offset, scale=1.0, angle=0.0):
        surf.blit(self.img, r := self.img.get_rect(center=self.pos))
