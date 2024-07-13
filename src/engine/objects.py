from operator import attrgetter
from typing import Union, Sequence

import pygame.event
import pymunk

from src.engine.base import BaseStructure
from src.engine.camera import Camera
from src.engine.config import *
from src.engine.utils import *
from src.engine.video import Renderer


class BaseObject(BaseStructure):
    def __init__(self, x=0.0, y=0.0, z=LAYERS.OBJECTS_LAYER):
        self.x, self.y = x, y
        self.alive = True
        self.z = z  # for sorting
        self.object_manager: Union[ObjectManager, None] = None
        self.first_render = False

    def on_ready(self):
        pass

    def on_renderer_ready(self, renderer: Renderer):
        pass

    def destroy(self):
        self.alive = False

    def constrain_to_rect(self, rect: pygame.Rect):
        self_rect = self.rect
        if self.x - self_rect.w / 2 < rect.left:
            self.x = self_rect.w / 2
        if self.x + self_rect.w / 2 > rect.right:
            self.x = Config.WIDTH - self_rect.w / 2
        if self.y - self_rect.h / 2 < rect.top:
            self.y = self_rect.h / 2
        if self.y + self_rect.h / 2 > rect.bottom:
            self.y = Config.HEIGHT - self_rect.h / 2

    @staticmethod
    def post_event(event, **kwargs):
        pygame.event.post(pygame.event.Event(event, kwargs))

    @property
    def pos(self):
        return Point(self.x, self.y)

    @pos.setter
    def pos(self, position):
        self.move_to(*position)

    @property
    def rect(self) -> pygame.Rect:
        return self.get_rect()

    def get_rect(self):
        raise NotImplementedError

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def move_to(self, x, y):
        dx, dy = x - self.x, y - self.y
        self.move(dx, dy)

    def draw_glow(self, surf: pygame.Surface, offset):
        pass

    def draw_overlay(self, surf: pygame.Surface, offset):
        pass

    def render_glow(self, renderer: Renderer, offset, scale=1.0, angle=0.0):
        pass

    def render_overlay(self, renderer: Renderer, offset, scale=1.0, angle=0.0):
        pass

    def interact(self, objects: list['BaseObject']):
        pass


class TimerObject(BaseObject):
    # these timers adjust according to FPS so that slow-mo effects can be done
    def __init__(self, timeout, action=None, oneshot=False):
        super().__init__(0, 0)
        self.t = time.time()
        self.ticks = 0
        self.timeout = timeout
        self.action = action
        self.oneshot = oneshot

    def reset(self):
        self.t = time.time()
        self.ticks = 0

    def update(self, events: list[pygame.event.Event], dt):
        if self.ticks >= float(self.timeout):
            while self.ticks >= float(self.timeout):
                if self.oneshot:
                    self.destroy()
                if self.action:
                    self.action()
                self.ticks -= float(self.timeout)
            # self.ticks = 0
        self.ticks += dt / Config.TARGET_FPS


class AnimatedSpriteObject(BaseObject):
    def __init__(self, x, y, z, sheet, rows, cols, images=None, alpha=True, scale=1.0, flipped=(0, 0),
                 color_key=None, timer=0.1, mode: Literal['center', 'topleft'] = 'center', smooth=False):
        self.sheet = LoopingSpriteSheet(
            sheet, rows, cols, images,
            alpha, scale, flipped, color_key, timer, mode, smooth
        )
        self.angle = 0
        self.scale = 1
        super().__init__(x, y, z)

    def draw(self, surf: pygame.Surface, offset, scale=1.0, angle=0.0):
        self.sheet.draw(surf, *(self.pos + offset), self.angle + angle, self.scale + scale)


class PeekInSprite(BaseObject):
    def __init__(self, sprite: pygame.Surface, vec=(0, 0), timer=0.1, speed=5):
        super().__init__()
        self.vec = vec
        self.timer = Timer(timer)
        self.speed = speed
        self.sprite = sprite
        self.surf = pygame.Surface([*self.sprite.get_size()], pygame.SRCALPHA)
        self.c_x = 0
        self.c_v = 0
        self.x_done = False
        self.y_done = False

    def rect(self) -> pygame.Rect:
        return self.surf.get_rect()

    @property
    def done(self):
        return self.x_done and self.y_done

    @property
    def image(self):
        if self.x_done and self.y_done:
            return self.surf
        self.surf = pygame.Surface([*self.sprite.get_size()], pygame.SRCALPHA)
        pos = [self.vec[0] * self.sprite.get_width(), self.vec[1] * self.sprite.get_height()]
        pos[0] -= self.c_x * self.vec[0]
        pos[1] -= self.c_v * self.vec[1]
        self.surf.blit(self.sprite, pos)
        return self.surf

    def skip(self):
        self.c_x = self.sprite.get_width()
        self.x_done = True
        self.c_v = self.sprite.get_height()
        self.y_done = True

    def update(self, events: list[pygame.event.Event], dt):
        if self.timer.tick:
            self.c_v += self.speed
            self.c_x += self.speed
            if self.c_x >= self.sprite.get_width():
                self.c_x = self.sprite.get_width()
                self.x_done = True
            if self.c_v >= self.sprite.get_height():
                self.c_v = self.sprite.get_height()
                self.y_done = True


class TrailStamp(BaseObject):
    def __init__(self, x, y, surf: pygame.Surface, alpha_rate=20):
        super().__init__(x, y)
        self.surf = surf
        self.alpha = 255
        self.alpha_rate = alpha_rate

    def update(self, events: list[pygame.event.Event], dt):
        self.alpha -= self.alpha_rate * dt
        self.alpha = clamp(self.alpha, 0, 255)
        if self.alpha <= 0:
            self.alive = False
        else:
            self.surf.set_alpha(self.alpha)

    def draw(self, surf: pygame.Surface, offset, scale=1.0, angle=0.0):
        surf.blit(self.surf, self.surf.get_rect(center=self.pos))


class ValueAnimator(BaseObject):
    def __init__(self, value):
        super().__init__(0, 0, 0)
        self.value = value
        self.next_anim = []
        self.target = self.value
        self.rate = 0.1
        self.action = None

    def reset(self, value=None):
        if value:
            self.value = value
        self.target = self.value
        self.next_anim.clear()

    def new_anim(self, target, rate, action):
        self.next_anim.append([target, rate, action])

    def then(self, action):
        self.new_anim(None, None, action)

    def set(self, value, action=None):
        return self.lerp(value, 1, action)

    def lerp(self, to, by=0.5, action=None):
        self.new_anim(to, by, action)
        return self

    def update(self, events: list[pygame.event.Event], dt):
        if self.rate == 1:
            self.value = self.target
        else:
            self.value = lerp(self.value, self.target, (1 - (1 - self.rate) ** dt))
        if abs(self.target - self.value) <= 0.01:
            self.value = self.target
            if self.action:
                self.action()
                self.action = None
            if self.next_anim:
                target, rate, action = self.next_anim.pop(0)
                self.action = action
                self.target, self.rate = target, rate


class AnimationStateObject(BaseObject):
    def __init__(self, sheet_path, rows, cols, images, state_info: dict, scale=1.0, timer=0.1):
        super().__init__(0, 0, LAYERS.OBJECTS_LAYER)
        self.timer = TimerObject(timer, action=self.on_timer_tick)
        self.sheet_info = sheet_path, rows, cols, images
        self.images = []
        self.state_info = state_info
        self.default_timeout = timer
        self.curr_state = next(iter(self.state_info.keys()))
        self.curr_frame = 0
        self.curr_frame_index = 0
        self.scale = scale
        self.flip = [0, 0]
        self.callback = None
        self.lock = False
        self._draw = True

    def on_frame_update(self):
        pass

    def destroy(self):
        super().destroy()
        self._draw = False

    def get_rect(self):
        if not self.images:
            return pygame.Rect(0, 0, 0, 0)
        rect = self.images[0].get_rect().scale_by(self.scale)
        rect.center = self.pos
        return rect

    def run_once(self, anim, callback=None, lock_until_done=True, force=True):
        self.switch_anim(anim, force)
        self.callback = callback
        self.lock = lock_until_done

    def switch_anim(self, anim, force=False):
        if self.lock:
            return
        if anim in self.state_info and (force or anim != self.curr_state):
            self.curr_frame = -1  # because on_timer_tick increments frame
            self.curr_state = anim
            self.on_timer_tick()
            self.timer.reset()

    def on_timer_tick(self):
        self.curr_frame += 1
        self.on_frame_update()
        if self.curr_frame > len(self.state_info[self.curr_state]) - 1:
            self.curr_frame = 0
            self.lock = False
            if self.callback:
                self.callback()
                self.callback = None
        index = self.state_info[self.curr_state][self.curr_frame]
        if isinstance(index, Sequence):
            self.curr_frame_index, self.timer.timeout = index
        else:
            self.curr_frame_index, self.timer.timeout = index, self.default_timeout

    def on_renderer_ready(self, renderer: Renderer):
        self.images = renderer.load_spritesheet(*self.sheet_info)

    def update(self, events: list[pygame.event.Event], dt):
        self.timer.update(events, dt)

    def render(self, renderer: Renderer, offset, scale=1.0, angle=0.0):
        if not self._draw:
            return
        img = self.images[self.curr_frame_index - 1]  # subtracting 1 because we start counting from 1 for spritesheets
        img.render(*(self.pos + offset), angle, self.scale * scale, self.flip)


class ObjectManager(BaseStructure):
    def __init__(self):
        self.objects: list[BaseObject] = []
        self._to_add: list[BaseObject] = []
        self.collision_enabled = True
        self.scene = None
        self.camera = Camera()
        from src.engine.physics import PhysicsManager
        self.physics_manager = PhysicsManager()

    def get_objects(self, instance):
        return (i for i in self.objects if isinstance(i, instance))

    def create_walls_around_rect(self, rect, thickness, draw=False):
        walls = self.physics_manager.create_walls_around_rect(rect, thickness)
        from src.engine.physics import PhysicsObject
        for wall in walls:
            body: pymunk.Body = wall[0]
            shape: pymunk.Poly = wall[1]
            p = PhysicsObject(body.position.x, body.position.y, shape.get_vertices(), 1000, pymunk.Body.STATIC, draw)
            self.add(p)

    def clear(self):
        self._to_add.clear()
        self.objects.clear()

    def add(self, _object: BaseObject):
        _object.object_manager = self
        self._to_add.append(_object)

    def add_multiple(self, _objects: list[BaseObject]):
        for i in _objects:
            self.add(i)

    def update(self, events: list[pygame.event.Event], dt):
        from src.engine.physics import PhysicsObject
        self.physics_manager.update(events, dt)
        if self._to_add:
            for i in self._to_add:
                i.on_ready()
                if isinstance(i, PhysicsObject):
                    i.on_physics_ready(self.physics_manager)
            self.objects.extend(self._to_add)
            self._to_add.clear()
        self.objects = [i for i in self.objects if i.alive]
        if Config.GAME_TOP_DOWN:
            self.objects.sort(key=attrgetter('z', 'y'))  # layers first, then y-sort (change if required)
        else:
            self.objects.sort(key=attrgetter('z'))
        self.camera.update(events, dt)
        for i in self.objects:
            if i.alive:
                i.interact(self.objects)
                i.update(events, dt)

    def draw(self, surf: pygame.Surface, offset, scale=1.0, angle=0.0):
        for i in self.objects:
            i.draw(surf, offset)

    def draw_glow(self, surf: pygame.Surface, offset=(0, 0)):
        for i in self.objects:
            i.draw_glow(surf, offset)

    def draw_overlay(self, surf: pygame.Surface, offset):
        for i in self.objects:
            i.draw_overlay(surf, offset)

    def render(self, renderer: Renderer, offset, scale=1.0, angle=0.0):
        offset += self.camera.get_offset()
        scale *= self.camera.zoom
        angle += self.camera.rotation
        for i in self.objects:
            pos = i.pos
            if not i.first_render:
                i.first_render = True
                i.on_renderer_ready(renderer)
            center = [Config.WIDTH / 2, Config.HEIGHT / 2]
            i.render(renderer, (((pos - offset).rotate(angle)) * scale) - pos + center, scale, angle)

    def render_glow(self, renderer: Renderer, offset, scale=1.0, angle=0.0):
        offset += self.camera.get_offset()
        scale *= self.camera.zoom
        angle += self.camera.rotation
        for i in self.objects:
            pos = i.pos
            if not i.first_render:
                i.first_render = True
                i.on_renderer_ready(renderer)
            center = [Config.WIDTH / 2, Config.HEIGHT / 2]
            i.render_glow(renderer, (((pos - offset).rotate(angle)) * scale) - pos + center, scale, angle)

    def render_overlay(self, renderer: Renderer, offset, scale=1.0, angle=0.0):
        offset += self.camera.get_offset()
        scale *= self.camera.zoom
        angle += self.camera.rotation
        for i in self.objects:
            pos = i.pos
            if not i.first_render:
                i.first_render = True
                i.on_renderer_ready(renderer)
            center = [Config.WIDTH / 2, Config.HEIGHT / 2]
            i.render_overlay(renderer, (((pos - offset).rotate(angle)) * scale) - pos + center, scale, angle)
