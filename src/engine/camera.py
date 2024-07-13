from typing import Sequence

import pygame

from src.engine.config import *
from src.engine.base import BaseStructure
from src.engine.utils import *


class Camera(BaseStructure):
    def __init__(self):
        self.zoom = 1.0
        self.offset = pygame.Vector2(0, 0)
        self.rotation = 0.0
        self.zoom_smooth_factor = 0.4
        self.offset_smooth_factor = 0.01
        self.rotation_smooth_factor = 0.4
        self.target_zoom = self.zoom
        self.target_offset = self.offset
        self.target_rotation = self.rotation
        self.shake_intensity = 0

    def update(self, events: list[pygame.event.Event], dt):
        for e in events:
            if e.type == EVENTS.CAMERA_UPDATE:
                try:
                    pos = e.pos
                    if pos:
                        self.set_position(*pos if isinstance(pos, Sequence) else [pos])
                except AttributeError:
                    pass
                try:
                    scale = e.scale
                    if scale:
                        self.set_zoom(*scale if isinstance(scale, Sequence) else [scale])
                except AttributeError:
                    pass
                try:
                    rot = e.rot
                    if rot is not None:
                        self.set_rotation(*rot if isinstance(rot, Sequence) else [rot])
                except AttributeError:
                    pass
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_p:
                    self.camera_shake(10)
            if e.type == EVENTS.CAMERA_SHAKE:
                self.camera_shake(e.intensity)
        self.zoom = lerp(self.zoom, self.target_zoom, self.zoom_smooth_factor * dt)
        self.rotation = lerp(self.rotation, self.target_rotation, self.rotation_smooth_factor * dt)
        self.offset = self.offset.lerp(self.target_offset, clamp(self.offset_smooth_factor * dt, 0, 1))
        self.shake_intensity *= 0.9 ** dt
        if self.shake_intensity <= 0.1:
            self.shake_intensity = 0
        # if Config.PLATFORM_WEB:
        #     self.rotation = 0  # very slow for software rendering (when used with default.tmpl)

    def camera_shake(self, intensity):
        self.shake_intensity = intensity

    def set_zoom(self, zoom, factor=None, force=False):
        if factor:
            self.zoom_smooth_factor = factor
        self.target_zoom = zoom
        if force:
            self.zoom = self.target_zoom

    def set_rotation(self, rotation, factor=None):
        if factor:
            self.rotation_smooth_factor = factor
        self.target_rotation = rotation

    def increase_zoom(self, by=1.0):
        self.target_zoom += by

    def increase_rotation(self, by=1.0):
        self.target_rotation += by

    def set_position(self, position, factor=None, force=False):
        if factor:
            self.offset_smooth_factor = factor
        self.target_offset = pygame.Vector2(*position)
        if force:
            self.offset = self.target_offset

    def move(self, dx, dy, factor=None):
        self.set_position(self.offset + pygame.Vector2(dx, dy).rotate(-self.rotation), factor)

    def get_offset(self):
        return self.offset + pygame.Vector2(get_random(-1, 1), get_random(-1, 1)) * self.shake_intensity
