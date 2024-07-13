import math
from operator import itemgetter
from typing import Optional

import pymunk

from src.engine.config import *
from src.engine.objects import BaseObject, BaseStructure, TimerObject
from src.engine.utils import Timer, LoopingSpriteSheet
from src.engine.video import Renderer


class PhysicsObject(BaseObject):
    def __init__(self, x, y, points, mass=150, body_type=pymunk.Body.DYNAMIC, draw=True, timer='inf', color='white'):
        super().__init__(x, y)
        self._draw = draw
        moment = pymunk.moment_for_poly(mass, points, (0, 0))
        self.body = pymunk.Body(mass=mass, moment=moment, body_type=body_type)
        self.body.position = (x, y)
        self.shape = pymunk.Poly(self.body, points)

        left, right = min(points, key=itemgetter(0)), max(points, key=itemgetter(0))
        top, bottom = min(points, key=itemgetter(1)), max(points, key=itemgetter(1))
        self.width = right[0] - left[0]
        self.height = bottom[1] - top[1]

        self.timer = TimerObject(timer, action=self.destroy, oneshot=True)
        self.color = color

        self.extra_shapes = []

    def on_ready(self):
        self.object_manager.add(
            self.timer
        )

    def on_physics_ready(self, physics_manager: 'PhysicsManager'):
        physics_manager.add(self.body, self.shape, *self.extra_shapes)

    @staticmethod
    def create_wall(x, y, size):
        points = [(-size[0] // 2, -size[1] // 2), (-size[0] // 2, size[1] // 2), (size[0] // 2, size[1] // 2),
                  (size[0] // 2, -size[1] // 2)]
        obj = PhysicsObject(x, y, points, mass=10000, body_type=pymunk.Body.STATIC, draw=False)
        obj.shape.friction = 0.25
        return obj

    @property
    def pos(self):
        self.x, self.y = self.body.position
        return pygame.Vector2(*self.body.position)

    @pos.setter
    def pos(self, value):
        self.move_to(*value)

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.body.position.x - self.width // 2, self.body.position.y - self.height // 2, self.width,
                           self.height)

    def destroy(self):
        super().destroy()
        self.unregister_from_physics_space()

    def unregister_from_physics_space(self):
        try:
            self.body.space.remove(self.body, self.shape)
        except AssertionError:
            pass

    def move(self, dx, dy):
        super().move(dx, dy)
        if self.body.body_type == pymunk.Body.STATIC:
            self.body.position = (self.body.position[0] + dx, self.body.position[1] + dy)
            for shape in self.body.shapes:
                shape.cache_bb()

    def draw(self, surf: pygame.Surface, offset, scale=1.0, angle=0.0):
        if not self._draw:
            return
        angle = self.shape.body.angle
        angle = math.degrees(angle)
        vertices = self.shape.get_vertices()
        vertices = [pygame.Vector2(i[0], i[1]) for i in vertices]
        vertices = [(i.rotate(angle) + self.pos + offset) for i in vertices]
        pygame.draw.polygon(surf, self.color, vertices)

    def render(self, renderer: Renderer, offset, scale=1.0, angle=0.0):
        if not self._draw:
            return
        angle = self.shape.body.angle + math.radians(angle)
        angle = math.degrees(angle)
        vertices = self.shape.get_vertices()
        vertices = [pygame.Vector2(i[0], i[1]) for i in vertices]
        vertices = [((i * scale).rotate(angle) + self.pos + offset) for i in vertices]
        renderer.polygon(vertices, self.color, True)


class SpritePhysicsObject(PhysicsObject):
    def __init__(self, x, y, sprite_sheet, rows, cols, images, mass, scale=1, timer='inf', flipped=(0, 0),
                 body_type=pymunk.Body.DYNAMIC):
        self.sheet = LoopingSpriteSheet(sprite_sheet, rows, cols, images, scale=scale, flipped=flipped)
        w, h = self.sheet.size
        self.mask = pygame.mask.from_surface(self.sheet.image, 50)
        points = [(i[0] - w / 2, i[1] - h / 2) for i in self.mask.outline(10)]
        self.outline = points
        super().__init__(x, y, points, mass, timer=timer, body_type=body_type)
        self._draw = False
        self.shape.friction = 0.5
        self.shape.elasticity = 0.5

    def draw(self, surf: pygame.Surface, offset, scale=1.0, angle=0.0):
        super().draw(surf, offset)
        self.sheet.draw(surf, *(self.pos + offset), math.degrees(-self.body.angle))
        # pygame.draw.polygon(
        #     surf, 'red', [[i[0] + self.pos.x, i[1] + self.pos.y] for i in self.shape.get_vertices()], 5
        # )


class PhysicsManager(BaseStructure):
    def __init__(self):
        self.space = pymunk.Space()

    def gravity(self):
        return self.space.gravity

    def create_walls_around_rect(self, rect, thickness):
        """
        Create static rectangular walls around a given rectangular area, outside of the actual rectangle.

        Parameters:
        rect (pygame.Rect): The rectangular area to create walls around.
        thickness (int): The thickness of the walls.
        """
        # Define the corners of the rectangle
        left = rect.left - thickness
        right = rect.right + thickness
        top = rect.top - thickness
        bottom = rect.bottom + thickness

        # Define the walls as static boxes (rectangles)
        walls = [
            self.create_static_box(left, top - thickness, rect.width + 2 * thickness, thickness),  # Top wall
            self.create_static_box(right, top, thickness, rect.height + 2 * thickness),  # Right wall
            self.create_static_box(left, bottom, rect.width + 2 * thickness, thickness),  # Bottom wall
            self.create_static_box(left - thickness, top, thickness, rect.height + 2 * thickness)  # Left wall
        ]

        return walls

    @staticmethod
    def create_static_box(x, y, width, height):
        """
        Create a static box (rectangle) with a given position and dimensions.

        Parameters:
        x (float): The x-coordinate of the box's center.
        y (float): The y-coordinate of the box's center.
        width (float): The width of the box.
        height (float): The height of the box.

        Returns:
        Box: A static box object with a body and shape.
        """
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        body.position = (x + width / 2, y + height / 2)
        shape = pymunk.Poly.create_box(body, (width, height))
        shape.friction = 1.0
        shape.elasticity = 0.7
        return [body, shape]

    def add(self, *objects: pymunk.Shape | pymunk.Body):
        self.space.add(*objects)

    def bodies_within_range(self, point, dist):
        bodies = []
        for info in self.space.point_query(point, dist, pymunk.ShapeFilter()):
            if info.shape and info.shape.body not in bodies:
                bodies.append(info.shape.body)
        return bodies

    def clear(self):
        self.space.remove(*self.space.bodies, *self.space.shapes)

    def update(self, events: list[pygame.event.Event], dt):
        self.space.step(dt / Config.TARGET_FPS)
