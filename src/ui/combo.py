from src.ui.ui_text import *


class Combo(UI):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.combo = 0

    def update(self, events: list[pygame.event.Event], dt):
        for e in events:
            if e.type == COMBO_ADD:
                self.combo += 1
                if self.combo >= 3:
                    self.object_manager.add(
                        UIText(Config.WIDTH / 2, Config.HEIGHT / 2, f'+{self.combo}', 50, 'green')
                    )
            if e.type == COMBO_DESTROY:
                if self.combo >= 5:
                    self.object_manager.add(
                        UIText(Config.WIDTH / 2, Config.HEIGHT / 2, f'COMBO: {self.combo}', 75, 'red')
                    )
                self.combo = 0
