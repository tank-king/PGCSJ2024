import asyncio
from pathlib import Path

import pygame

from src.engine.config import *
from src.engine.scene import SceneManager
from src.engine.sounds import SoundManager
from src.engine.utils import clamp, text
from src.engine.video import Renderer


def init():
    parent = Path(__file__).parent
    sys.path.append(parent.absolute().__str__())

    try:
        pygame.mixer.init()
        pygame.mixer.set_num_channels(128)
        GAMESTATS.SPEAKERS_INIT = True
        SoundManager.load_sounds()
    except pygame.error:
        GAMESTATS.SPEAKERS_INIT = False
        try:
            pygame.init()
        except pygame.error:
            pass

    pygame.init()


class Game:
    def __init__(self):
        init()
        flags = pygame.SCALED | pygame.FULLSCREEN
        full_screen = False
        if Config.SDL_VERSION == 1:
            if full_screen:
                self.screen = pygame.display.set_mode([Config.WIDTH, Config.HEIGHT], flags)
            else:
                self.screen = pygame.display.set_mode([Config.WIDTH, Config.HEIGHT], pygame.SCALED)
            self.window = pygame.Window.from_display_module()
            pygame.display.set_caption(Config.GAME_NAME)
        else:
            self.screen = None
            from pygame._sdl2.video import Window
            self.window = Window(Config.GAME_NAME, [Config.WIDTH, Config.HEIGHT], opengl=True)
        # pygame.key.set_repeat(500, 10)

        # win_handle = sdl2_lib.SDL_GetWindowFromID(ctypes.c_uint32(self.window.id))
        self.full_screen = False
        if Config.SDL_VERSION == 1:
            self.renderer = None
        else:
            self.renderer = Renderer(self.window, vsync=Config.VSYNC)

        # self.renderer.print_render_drivers()

        self.manager = SceneManager()
        self.clock = pygame.time.Clock()

    def toggle_full_screen(self):
        self.full_screen = not self.full_screen
        if Config.SDL_VERSION == 1:
            if self.full_screen:
                self.screen = pygame.display.set_mode([Config.WIDTH, Config.HEIGHT], pygame.SCALED | pygame.FULLSCREEN)
            else:
                self.screen = pygame.display.set_mode([Config.WIDTH, Config.HEIGHT], pygame.SCALED)
        else:
            self.renderer.toggle_full_screen()

    async def run(self):
        dt = 1
        fps = Config.FPS * 1
        while True:
            events = pygame.event.get()
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            for e in events:
                if e.type == pygame.QUIT:
                    sys.exit(0)
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_f:
                        self.toggle_full_screen()
                    # if e.key == pygame.K_ESCAPE:
                    #     sys.exit(0)
                    if e.key == pygame.K_c:
                        if fps == Config.FPS:
                            fps = 0
                        else:
                            fps = Config.FPS
                if e.type == EVENTS.MOUSE_HOVERED:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            await asyncio.sleep(0)
            self.manager.update(events, dt)
            if Config.SDL_VERSION == 1:
                self.manager.draw(self.screen, (0, 0))
                t = text(int(self.clock.get_fps()).__str__(), color='white')
                self.screen.blit(t, [0, 0])
                GAMESTATS.MOUSE_POS = pygame.mouse.get_pos()
                pygame.display.update()
            else:
                self.manager.render(self.renderer, (0, 0))
                # if Config.SHOW_FPS:
                #     self.renderer.text(int(self.clock.get_fps()).__str__(), 50, 'white', [0, 0], 'topleft')
                # self.renderer.text(GAMESTATS.MOUSE_POS.__str__(), Config.SMALL_TEXT, 'white', [Config.WIDTH, 0], 'topright')
                # self.renderer.text(self.window.size.__str__(), Config.SMALL_TEXT, 'white', [Config.WIDTH, Config.SMALL_TEXT], 'topright')
                for e in events:
                    if e.type == pygame.MOUSEMOTION:
                        GAMESTATS.MOUSE_POS = e.pos
                self.renderer.present()
            SoundManager.update()
            self.clock.tick(fps)
            try:
                dt = Config.TARGET_FPS / self.clock.get_fps()
            except ZeroDivisionError:
                dt = 1
            dt = clamp(dt * Config.TIME_SCALE, 0.01, 6)
