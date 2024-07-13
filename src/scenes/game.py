import pygame

from src.engine.scene import Scene
from src.engine.sounds import SoundManager
from src.engine.utils import *
from src.engine.video import Renderer
from src.objects.bullet import Bullet

from src.objects.space_station import *
from src.objects.player import Player


class Planet(BaseObject):
    def __init__(self, x, y):
        super().__init__(x, y, -1)
        self.img: Image | None = None

    def on_renderer_ready(self, renderer: Renderer):
        img = renderer.load_image(get_path('images', 'space', 'planet4.png'))
        self.img = Image(img, img.get_rect())

    def render(self, renderer: Renderer, offset, scale=1.0, angle=0.0):
        self.img.render(*(self.pos + offset * 0.75), angle, scale * 1)


class Dust(BaseObject):
    def __init__(self, x, y):
        super().__init__(x, y, -1)
        self.img: Image | None = None

    def on_renderer_ready(self, renderer: Renderer):
        img = renderer.load_image(get_path('images', 'space', 'dust.png'))
        self.img = Image(img, img.get_rect())

    def render(self, renderer: Renderer, offset, scale=1.0, angle=0.0):
        self.img.render(*(self.pos + offset * 0.4), angle, scale * 2.5)


class Game(Scene):
    def __init__(self, manager, name):
        super().__init__(manager, name)
        self.object_manager.create_walls_around_rect(Config.SCREEN_RECT, 50)
        x, y = Config.WIDTH / 2, Config.HEIGHT / 2

        self.object_manager.add_multiple(
            [
                Dust(x, y),
                Planet(x, y),
                SpaceStation(x, y),
                p := Player(x, y * 1.5)
            ]
        )
        self.camera.set_position([x, y], force=True)
        self.camera.set_zoom(1, factor=0.1, force=True)
        self.player = p
        self.tex = None

        self.camera_zoom = 1

    def enter(self):
        SoundManager.play_bg('music.ogg', loops=-1, volume=25)

    def update(self, events: list[pygame.event.Event], dt):
        super().update(events, dt)
        for e in events:
            if e.type == pygame.MOUSEWHEEL:
                self.camera.set_zoom(clamp(self.camera.zoom + e.y / 4, 0.75, 10))
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_q:
                    self.camera_zoom += 1
                    self.camera_zoom %= 3
        self.camera.set_zoom(self.camera_zoom + 1)
        keys = pygame.key.get_pressed()
        # if keys[pygame.K_RIGHT]:
        #     self.camera.increase_rotation(1 * dt)
        # if keys[pygame.K_LEFT]:
        #     self.camera.increase_rotation(-1 * dt)
        # self.camera.set_rotation(-self.player.angle - 90, 0.1)
        self.camera.set_position(self.player.pos, 0.1)
        c = 0
        for i in self.object_manager.get_objects(Bullet):
            c += 1
        # print(c)

    def render(self, renderer: Renderer, offset, scale=1.0, angle=0.0):
        renderer.fill('black')
        super().render(renderer, offset, scale, angle)
        renderer.text(f'{(c := len([*self.object_manager.get_objects(SpriteComponent)]))} Remaining', Config.MEDIUM_TEXT, 'white', [5, 5], 'topleft')
        if c == 0:
            renderer.text('Destroyed All Components!', Config.LARGE_TEXT, 'white', [Config.WIDTH / 2, Config.HEIGHT / 2])
            renderer.text('Press R to Replay!', Config.SMALL_TEXT, 'white', [Config.WIDTH / 2, Config.HEIGHT / 2 + 100])
