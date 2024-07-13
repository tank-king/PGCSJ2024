import math
import string
from functools import lru_cache

import pygame
from pygame._sdl2 import video

from src.engine.config import *
from src.engine.utils import *


class Texture(video.Texture):
    pass


class Image(video.Image):
    def __init__(self, texture_or_image, srcrect):
        super().__init__(texture_or_image, srcrect)
        self.dstrect = self.srcrect

    def get_rect(self, **kwargs):
        rect = super().get_rect()
        for i in kwargs:
            rect.__setattr__(i, kwargs[i])
        return rect

    def scale_by(self, amt):
        rect = self.get_rect().scale_by(amt)
        img = Image(self.texture, self.srcrect)
        img.dstrect = rect
        return img

    def rotate_to(self, angle, origin=None):
        img = Image(self.texture, self.srcrect)
        img.angle = angle
        img.origin = origin
        return img

    def render(self, x, y, angle=0.0, scale=1.0, flip=(0, 0), anchor='center'):
        img = self
        self.angle = angle
        img.dstrect = img.srcrect.scale_by(scale)
        img.dstrect.__setattr__(anchor, (x, y))
        img.flip_x, img.flip_y = flip
        img.draw(None, img.dstrect)


class Renderer(video.Renderer):
    class TEXTURES:
        # textures
        (
            SQUARE_TEX,
            SCREEN_TEX,
            *_,
        ) = range(20)

    def __init__(self, window: video.Window, vsync=False):
        self.window = window
        super().__init__(window, vsync=vsync, target_texture=True, index=-1)
        width, height = window.size
        self.size = [width, height]
        self.logical_size = [width, height]
        self.textures = {
            Renderer.TEXTURES.SQUARE_TEX: self.square_tex(),
            Renderer.TEXTURES.SCREEN_TEX: self.screen_tex(),
        }
        self.text_atlases = {}
        self.full_screen = False

    @staticmethod
    def render_drivers():
        return video.get_drivers()

    def print_render_drivers(self):
        print(*self.render_drivers(), sep='\n')

    def fill(self, color):
        # self.draw_color = pygame.Color('black')
        # self.clear()

        # this is done for having black bars in fullscreen mode
        self.textures[Renderer.TEXTURES.SQUARE_TEX].color = pygame.Color(color)
        rect = pygame.Rect(*self.size, *self.logical_size)
        rect.center = [self.size[0] / 2, self.size[1] / 2]
        self.blit(self.textures[Renderer.TEXTURES.SQUARE_TEX], rect)

    def get_mouse_pos(self):
        rect = pygame.Rect(*self.size, *self.logical_size)
        rect.center = [self.size[0] / 2, self.size[1] / 2]
        return pygame.Vector2(*pygame.mouse.get_pos()) - [*rect.topleft]

    def square_tex(self):
        s = pygame.Surface([64, 64])
        s.fill('white')
        return Texture.from_surface(self, s)

    def screen_tex(self):
        return Texture(self, [Config.WIDTH, Config.HEIGHT], target=True, scale_quality=Config.DEFAULT_TEXTURE_QUALITY)

    def gen_text_tex(self, size, outline=0, max_tex_size=1024):
        def text_func(msg):
            if outline:
                return text_with_outline(msg, size, 'white', 'black', outline)
            else:
                return text(msg, size, 'white')
        chars = {
            i: text_func(i)
            for i in string.printable if i == ' ' or i not in string.whitespace
        }
        texture = Texture(self, [max_tex_size, max_tex_size], static=True, scale_quality=Config.DEFAULT_TEXTURE_QUALITY)
        texture.blend_mode = pygame.BLENDMODE_BLEND
        surface = pygame.Surface([max_tex_size, max_tex_size], pygame.SRCALPHA)
        surface.set_colorkey('black')
        x = y = max_h = 0
        images = {}
        for char, surf in chars.items():
            if x + surf.get_width() > max_tex_size:
                x = 0
                y += max_h
            if y + surf.get_height() > max_tex_size:
                raise ValueError(f"Unable to fit all text in texture of size = {max_tex_size}")
            surface.blit(surf, [x, y])
            max_h = max(max_h, surf.get_height())
            rect = pygame.Rect(x, y, *surf.get_size())
            images[char] = Image(texture, rect)
            x += surf.get_width()
        texture.update(surface)
        self.text_atlases[size] = images

    def text(self, msg, size, color, pos, anchor='center', outline=0, wraplength=0):
        if not isinstance(msg, str):
            msg = str(msg)
        if size not in self.text_atlases:
            self.gen_text_tex(size, outline)
        images = self.text_atlases[size]
        rect = pygame.Rect(*pos, *text_size_with_outline(msg, size, outline))
        rect.__setattr__(anchor, pos)
        x, y = rect.topleft
        for i in msg:
            img: Image = images[i]
            img.color = pygame.Color(color)
            img.draw(None, img.get_rect(topleft=[x, y]))
            x += img.get_rect().w

    def rect(self, color, rect, thickness=0):
        if not isinstance(rect, pygame.Rect):
            rect = pygame.Rect(rect)
        t = self.textures[Renderer.TEXTURES.SQUARE_TEX]
        t.color = pygame.Color(color)
        if thickness < 0:
            raise ValueError('Thickness should be >= 0')
        if thickness:
            t.draw(None, pygame.Rect(rect.x, rect.y - thickness / 2, rect.w, thickness))
            t.draw(None, pygame.Rect(rect.x, rect.y + rect.h - thickness / 2, rect.w, thickness))
            t.draw(None, pygame.Rect(rect.x - thickness / 2, rect.y, thickness, rect.h))
            t.draw(None, pygame.Rect(rect.x + rect.w - thickness / 2, rect.y, thickness, rect.h))
        else:
            t.draw(None, rect)

    def polygon(self, points, color, fill=False):
        assert len(points) >= 3
        self.draw_color = pygame.Color(color)
        p1 = points[0]
        for i in range(1, len(points) - 1):
            p2 = points[i]
            p3 = points[i + 1]
            if fill:
                self.fill_triangle(p1, p2, p3)
            else:
                self.draw_triangle(p1, p2, p3)

    def toggle_full_screen(self):
        if self.full_screen:
            self.window.set_windowed()
        else:
            self.window.set_fullscreen(True)
        self.full_screen = not self.full_screen

    def load_image(self, path) -> Texture:
        if path in self.textures:
            return self.textures[path]
        print(f'loading texture {path}')
        img = load_image(path)
        t = Texture.from_surface(self, img)
        self.textures[path] = t
        return t

    def load_spritesheet(self, path, rows, cols, images) -> list[Image]:
        tex = self.load_image(path)
        img = load_image(path)
        sheet = SpriteSheet(img, rows, cols, images)
        sheet.get_images()
        rects = sheet.get_rects()
        return [Image(tex, r) for r in rects]
