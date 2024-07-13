import pygame

from src.engine.scene import Scene
from src.engine.utils import *
from src.engine.video import Renderer
from src.objects.bullet import Bullet
from src.engine.sounds import SoundManager
from src.engine.objects import *

from src.objects.space_station import *
from src.objects.player import Player

_planet_name = 'Crimson Haven'
_agency_name = f'{_planet_name} Space Authority'
_player_company_name = 'AstraWreck'

_skip_ready = False


class Planet(BaseObject):
    def __init__(self, x, y):
        super().__init__(x, y, -1)
        self.img: Image | None = None

    def on_renderer_ready(self, renderer: Renderer):
        img = renderer.load_image(get_path('images', 'space', 'planet4.png'))
        self.img = Image(img, img.get_rect())

    def render(self, renderer: Renderer, offset, scale=1.0, angle=0.0):
        self.img.render(*(self.pos + offset * 0.75), angle, scale * 1)


class Desktop(BaseObject):
    def __init__(self, x, y):
        super().__init__(x, y, -1)
        self.img: Image | None = None

    def on_renderer_ready(self, renderer: Renderer):
        img = renderer.load_image(get_path('images', 'pc', 'desktop.png'))
        self.img = Image(img, img.get_rect())

    def render(self, renderer: Renderer, offset, scale=1.0, angle=0.0):
        self.img.render(*(self.pos + offset * 0.4), angle, scale * 4)


class MessageApp(BaseObject):
    def __init__(self, x=Config.WIDTH / 2, y=Config.HEIGHT / 2):
        super().__init__(x, y)
        self.box_scale = ValueAnimator(0.1).lerp(1, 0.25, lambda: self.__setattr__('draw_text', True))
        self.message = f"""
        Contract Offer:  Space Station Demolition
        From:  {_agency_name}
        Subject:  New Contract
        
        Message:
        "Dear {_player_company_name},
        Impressed by your previous demolition records,
        {_agency_name} offers you a contract
        to dismantle an obsolete space station orbiting 
        Mauve Terra. Details attached.
        
        Best regards,
        {_agency_name}"
        """
        self.message = '\n'.join(map(str.strip, self.message.split('\n')))
        self.draw_text = False
        self.c = 0
        self.timer = TimerObject(0.02, action=self.increment_c)
        self.message_speak = False

    def on_ready(self):
        SoundManager.play('popup')

    def increment_c(self):
        global _skip_ready
        self.c += 2
        if self.c >= len(self.message):
            self.c = len(self.message) - 1
            _skip_ready = True

    def update(self, events: list[pygame.event.Event], dt):
        self.box_scale.update(events, dt)
        if self.draw_text:
            if not self.message_speak:
                self.message_speak = True
                SoundManager.stop('contract_message')
                SoundManager.play('contract_message')
            self.timer.update(events, dt)

    def get_rect(self):
        r = pygame.Rect(0, 0, 800, 500)
        r.center = self.pos
        return r

    def render(self, renderer: Renderer, offset, scale=1.0, angle=0.0):
        renderer.rect([11] * 3, self.rect.scale_by(self.box_scale.value))
        renderer.rect([255] * 3, self.rect.scale_by(self.box_scale.value), 2)
        rect = self.rect
        messages = self.message[:self.c].split('\n')
        if self.draw_text:
            for i, msg in enumerate(messages):
                msg = msg.strip()
                renderer.text(msg, Config.SMALL_TEXT, 'white', [rect.left + 25, rect.top + i * (Config.SMALL_TEXT + 5)],
                              'topleft')
        if self.c == len(self.message) - 1:
            renderer.text('Press any key to skip...', Config.SMALL_TEXT, 'white',
                          [Config.WIDTH / 2, Config.HEIGHT - 10], 'midbottom')


class Notification(BaseObject):
    def __init__(self):
        super().__init__(0, Config.HEIGHT - 5)
        self.messages = [
            'Alert!', '',
            'You have an unread',
            'notification. Press any key.'
        ]
        self.target_x = ValueAnimator(0)
        self.open()
        self.done = False

    def on_ready(self):
        SoundManager.play('notification')

    def open(self):
        self.target_x.reset(0)
        self.target_x.set(Config.WIDTH - 5 + 450).lerp(Config.WIDTH - 5, 0.1)

    def close(self):
        self.target_x.reset(0)
        self.target_x.set(Config.WIDTH - 5).lerp(Config.WIDTH - 5 + 450, 0.1)

    def update(self, events: list[pygame.event.Event], dt):
        self.target_x.update(events, dt)
        self.x = self.target_x.value
        rect = pygame.Rect(0, 0, 400, 110)
        rect.bottomright = self.pos
        if not self.done:
            for e in events:
                if e.type == pygame.KEYDOWN:
                    self.done = True
                    self.object_manager.add(
                        MessageApp()
                    )
                    self.close()
                if e.type == pygame.MOUSEBUTTONDOWN:
                    if e.button == 1:
                        if rect.collidepoint(GAMESTATS.MOUSE_POS):
                            self.done = True
                            self.object_manager.add(
                                MessageApp()
                            )
                            self.close()

    def render(self, renderer: Renderer, offset, scale=1.0, angle=0.0):
        rect = pygame.Rect(0, 0, 400, 110)
        rect.bottomright = self.pos
        renderer.rect([11] * 3, rect, 0)
        renderer.rect([255] * 3, rect, 2)
        for i, msg in enumerate(self.messages):
            renderer.text(msg, Config.SMALL_TEXT, 'white', [rect.left + 5, rect.top + i * Config.SMALL_TEXT], 'topleft')


class AcceptContract(Scene):
    def __init__(self, manager, name):
        super().__init__(manager, name)
        self.object_manager.create_walls_around_rect(Config.SCREEN_RECT, 50)
        x, y = Config.WIDTH / 2, Config.HEIGHT / 2

        self.object_manager.add_multiple(
            [
                Desktop(x, y),
                Notification(),
            ]
        )
        self.camera.set_position([x, y], force=True)
        # self.camera.set_zoom(1, force=True)
        self.tex = None

    def update(self, events: list[pygame.event.Event], dt):
        super().update(events, dt)
        if _skip_ready:
            for e in events:
                if e.type == pygame.KEYDOWN:
                    SoundManager.stop('contract_message')
                    self.manager.transition_manager.set_transition('square')
                    self.manager.switch_mode('game', reset=True, transition=True)

    def render(self, renderer: Renderer, offset, scale=1.0, angle=0.0):
        renderer.fill('black')
        super().render(renderer, offset, scale, angle)
