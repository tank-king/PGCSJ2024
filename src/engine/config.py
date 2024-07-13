import os
import platform
import sys

import pygame
from pygame._sdl2.video import SCALEQUALITY_BEST
from typing import Callable


# import ctypes.util
#
# sdl2_dll = ctypes.util.find_library("sdl2")
# sdl2_lib = ctypes.CDLL(sdl2_dll)
#
# sdl2_lib.SDL_GetError.restype = ctypes.c_char_p
# sdl2_lib.SDL_GetWindowFromID.restype = ctypes.POINTER(
#     type("SDL_Window", (ctypes.Structure,), {})  # noqa
# )
#
# sdl2_lib.SDL_Init(32)


class Config:
    SDL_VERSION = 2
    GAME_NAME = 'AstraWreck'
    ROOT_SCENE = 'acceptcontract'
    GAME_TOP_DOWN = False
    WIDTH = 1280  # width of the screen
    HEIGHT = 720  # height of the screen
    DEFAULT_TEXTURE_QUALITY = SCALEQUALITY_BEST
    SCREEN_RECT = pygame.Rect(0, 0, WIDTH, HEIGHT)
    SCREEN_COLLISION_RECT = SCREEN_RECT.inflate(100, 100)
    BG_COlOR = '#001018'
    TEXT_COLOR = '#511309'
    VOLUME = 100  # sound volume
    FPS = 120
    TARGET_FPS = 60
    VSYNC = False
    SHOW_FPS = True

    SMALL_TEXT = 25
    MEDIUM_TEXT = 50
    LARGE_TEXT = 75

    TIME_SCALE = 1

    PLATFORM_WEB = sys.platform == "emscripten"
    PIXELATED_ON_WEB = True

    @classmethod
    def center(cls):
        return pygame.Vector2(Config.WIDTH / 2, Config.HEIGHT / 2)


if Config.PLATFORM_WEB and Config.PIXELATED_ON_WEB:
    platform.window.canvas.style.imageRendering = "pixelated"

ASSETS = 'assets'


class EVENTS:
    (
        SONG_FINISHED_EVENT,
        HEALTHBAR_CHANGE,
        CAMERA_SHAKE,  # kwargs: intensity
        DISPLAY_SUBTITLE,  # kwargs: pos, time
        ADD_MONEY,
        MOUSE_HOVERED,
        COMBO_ADD,
        COMBO_DESTROY,
        FIGHTER_ATTACK,
        CAMERA_UPDATE,  # kwargs: [pos, [factor]], [scale, [factor]], [rot, [factor]]
        *_,
    ) = (pygame.event.custom_type() for _ in range(20))


class LAYERS:
    (
        BULLET_LAYER,
        OBJECTS_LAYER,
        PLAYER_LAYER,
        EXPLOSION_LAYER,
        FISH_LAYER,
        BUBBLE_LAYER,
        UI_LAYER,
        *_
    ) = range(0, 10)


class InputKeyMap:
    LEFT = pygame.K_LEFT
    RIGHT = pygame.K_RIGHT
    UP = pygame.K_UP
    DOWN = pygame.K_DOWN

    @classmethod
    def all_keys(cls):
        for i in dir(InputKeyMap):
            if not i.startswith('__'):
                val = cls.__getattribute__(cls, i)
                if not isinstance(val, classmethod):
                    yield val


class InputMap:
    pass


BASE_PATH = ''


class GAMESTATS:
    SPEAKERS_INIT = False
    MOUSE_POS = [0, 0]
    # OUTLINES = []


DEBUG = False

NUMPY = True
SCIPY = True

try:
    import numpy
except ImportError:
    numpy = ...
    NUMPY = False

try:
    import scipy
except ImportError:
    scipy = ...
    SCIPY = False

# for closing pyinstaller splash screen if loaded from bundle

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    print('running in a PyInstaller bundle')
    BASE_PATH = sys._MEIPASS
    ASSETS = os.path.join(sys._MEIPASS, ASSETS)
    try:
        import pyi_splash

        pyi_splash.close()
    except ImportError:
        pass
else:
    print('running in a normal Python process')
