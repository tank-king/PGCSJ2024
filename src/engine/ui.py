import time

from src.engine.objects import BaseStructure, BaseObject
from src.engine.config import *
from utils import *
import pygame

UI_SIZE = 30


class UI(BaseObject):
    def __init__(self, x, y):
        super().__init__(x, y, UI_LAYER)


class Button(BaseObject):
    def __init__(self, x=0, y=0, label='Button', action=None, text_size=30, anchor='topleft'):
        super().__init__(x, y, UI_LAYER)
        self.x = x
        self.y = y
        self.action = action
        self.label = label
        self.text = text(self.label, text_size, aliased=True)
        self.inactive_color = pygame.Color('#511309')
        self.active_color = self.inactive_color.lerp('white', 0.1)
        self.is_active = False
        self.anchor = anchor

    @property
    def rect(self) -> pygame.Rect:
        rect = self.text.get_rect()
        rect.__setattr__(self.anchor, self.pos)
        return rect

    def update(self, events: list[pygame.event.Event], dt):
        mx, my = pygame.mouse.get_pos()
        if self.rect.collidepoint(mx, my):
            self.is_active = True
        else:
            self.is_active = False
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1:
                    if self.is_active:
                        if self.action is not None:
                            self.action()

    def draw(self, surf: pygame.Surface, offset, scale=1.0, angle=0.0):
        color = self.active_color if self.is_active else self.inactive_color
        rect = self.text.get_rect()
        rect.__setattr__(self.anchor, self.pos)
        rect1 = rect.inflate(20, 20)
        pygame.draw.rect(surf, color, rect1)
        pygame.draw.rect(surf, 'black', rect1, 2)
        surf.blit(self.text, self.text.get_rect(center=rect.center))


class Label(BaseStructure):
    def __init__(self, x=0, y=0, w=100, h=50, label='Label'):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.label = label
        self.text = text(self.label, size=UI_SIZE, aliased=True)
        self.color = 'white'
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        self.is_active = False

    def draw(self, surf: pygame.Surface, offset, scale=1.0, angle=0.0):
        pygame.draw.rect(surf, self.color, (self.x, self.y, self.w, self.h), 5)
        surf.blit(self.text, self.text.get_rect(center=self.rect.center))


class InputBox(BaseStructure):
    def __init__(self, x=0, y=0, w=100, h=50, default='Type Here', initial_string='', label='none', extendable=True,
                 numeric_only=False):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        self.numeric_only = numeric_only
        self.active_color = 'blue'
        self.inactive_color = 'white'
        self.label = label
        self.default = default
        self.extendable = extendable
        self.is_active = False
        self.is_hovered = False
        self.text = initial_string
        self.allowed_input = 'abcdefghijklmnopqrstuvwxyz1234567890' if not self.numeric_only else '1234567890'
        self.cursor_visible = True
        self.cursor_blink_timer = time.time()

    def update(self, events: list[pygame.event.Event], dt):
        mx, my = pygame.mouse.get_pos()
        if self.rect.collidepoint(mx, my):
            self.is_hovered = True
        else:
            self.is_hovered = False
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1:
                    if self.is_hovered:
                        self.is_active = True
                    else:
                        self.is_active = False
            if e.type == pygame.KEYDOWN:
                if self.is_active:
                    if e.key == pygame.K_BACKSPACE:
                        self.text = self.text[:-1]
                    if not len(self.text) > self.w // 15 - 3:
                        if e.key == pygame.K_SPACE:
                            self.text += ' '
                        # elif e.key != pygame.KMOD_SHIFT and chr(e.key) in self.allowed_input:
                        #     self.text += chr(e.key).upper()
            if e.type == pygame.TEXTINPUT:
                if self.is_active:
                    if e.text.lower() in self.allowed_input:
                        if not len(self.text) > self.w // 15 - 3:
                            self.text += e.text

    def draw(self, surf: pygame.Surface, offset, scale=1.0, angle=0.0):
        color = self.active_color if self.is_hovered or self.is_active else self.inactive_color
        if self.is_active:
            display_text = self.text
        else:
            display_text = self.text if self.text != '' else self.default
        if self.is_active:
            if time.time() - self.cursor_blink_timer > 0.5:
                self.cursor_blink_timer = time.time()
                self.cursor_visible = not self.cursor_visible
            if self.cursor_visible:
                display_text += '_'
            else:
                display_text += ' '
        t = text(display_text, UI_SIZE, aliased=True)
        pygame.draw.rect(surf, color, self.rect, 5)
        surf.blit(t, t.get_rect(center=self.rect.center))
