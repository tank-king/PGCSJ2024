import pygame

from src.engine.objects import ValueAnimator
from src.objects.component import Component, BaseObject
from src.engine.video import Renderer, Image, Texture
from src.engine.utils import *
from src.objects.explosion import Explosion

_scale = 4


class SpaceComponent(Component):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.velocity = pygame.Vector2()
        self.angular_velocity = 0
        self.dismantled = False

    def get_min_components(self):
        return 2

    def dismantle(self):
        self.dismantled = True
        if self.parent:
            self.parent.remove_component(self)
        else:
            print(self)
        self.velocity = pygame.Vector2(1, 1).rotate(get_random(0, 360)) * get_random(0.1, 0.2)
        self.angular_velocity = get_random(-1, 1)

    def update(self, events: list[pygame.event.Event], dt):
        if self.components and all([(not i.alive) for i in self.components]):
            self.destroy()
        self.pos += self.velocity * dt
        self.angle += self.angular_velocity * dt
        center = pygame.Vector2(*Config.SCREEN_RECT.center)
        if center.distance_to(self.pos) >= 1000:
            self.velocity *= 0
        if not isinstance(self, SpriteComponent) and len(self.components) < self.get_min_components():
            self.destroy()


class SpriteComponent(SpaceComponent):
    def __init__(self, x, y, sprite, scale: float = _scale):
        super().__init__(x, y)
        self.img: Image | None = None
        self.sprite = sprite
        self.scale = scale
        self.health = self.damage_amt()
        self.scale_animator = ValueAnimator(self.scale)

    def on_ready(self):
        self.object_manager.add(self.scale_animator)

    def damage_amt(self):
        _ = self
        return 3

    def get_damage(self, amt: float = 0.0):
        if not self.dismantled:
            self.dismantle()
        self.health -= amt
        if self.health <= 0:
            self.destroy()
        rate = 0.25
        self.scale_animator.reset(self.scale)
        self.scale_animator.lerp(self.scale + 1, rate).lerp(self.scale, rate)

    def get_rect(self):
        return self.img.texture.get_rect(center=self.pos).scale_by(1.5)

    def on_renderer_ready(self, renderer: Renderer):
        img = renderer.load_image(get_path('images', 'space_station', self.sprite))
        self.img = Image(img, img.get_rect())

    def render(self, renderer: Renderer, offset, scale=1.0, angle=0.0):
        self.img.render(*(self.pos + offset), self.angle + angle, self.scale_animator.value * scale)

    def destroy(self):
        if not self.alive:
            super().destroy()
            return
        size = pygame.Vector2().distance_to([*self.img.get_rect().size]) * self.scale / 40
        self.object_manager.add(Explosion(*self.pos, size))
        self.scale_animator.destroy()
        super().destroy()


class PhotoVoltaicUnit(SpriteComponent):
    def __init__(self, x, y, optimization=0, scale=_scale):
        super().__init__(x, y, f'photovoltaic_array_{optimization}.png', scale)

    def damage_amt(self):
        return 3


class PhotoVoltaicArray(SpaceComponent):
    def __init__(self, x, y):
        super().__init__(x, y)
        # amount of optimizations needed for rendering (lowest is 0)
        optimization_level = 1
        for i in range(-12, 12, optimization_level + 1):
            self.add_component(
                PhotoVoltaicUnit(self.pos.x, self.pos.y + i * _scale * 2, optimization_level)
            )

    def get_min_components(self):
        return 5


class MiniPhotoVoltaicArray(SpaceComponent):
    def __init__(self, x, y, scale: float = _scale):
        super().__init__(x, y)
        for i in range(-10, 8):
            self.add_component(
                PhotoVoltaicUnit(self.pos.x, self.pos.y + i * scale * 2, scale=scale)
            )
        self.add_component(PhotoVoltaicBottomConnector(self.pos.x, self.pos.y + 9 * scale * 2, scale / 2))

    def get_min_components(self):
        return 5


class PhotoVoltaicTopConnector(SpriteComponent):
    def __init__(self, x, y):
        super().__init__(x, y, 'photovoltaic_array_top_connector.png', 2)


class PhotoVoltaicBottomConnector(SpriteComponent):
    def __init__(self, x, y, scale=2):
        super().__init__(x, y, 'photovoltaic_array_bottom_connector.png', scale)


class PhotoVoltaicMidConnector(SpriteComponent):
    def __init__(self, x, y):
        super().__init__(x, y, 'photovoltaic_array_mid_connector.png', 0.5)


class PhotoVoltaicEdge(SpriteComponent):
    def __init__(self, x, y):
        super().__init__(x, y, 'photovoltaic_array_edge.png', 2)


class PhotoVoltaicPanel(SpaceComponent):
    def __init__(self, x, y, angle=0):
        super().__init__(x, y)
        w = 4
        gap = 1.5
        offset = w + gap
        self.add_component(PhotoVoltaicArray(self.pos.x - _scale * offset, self.pos.y))
        self.add_component(PhotoVoltaicArray(self.pos.x + _scale * offset, self.pos.y))
        self.add_component(PhotoVoltaicTopConnector(self.pos.x, self.pos.y - 13 * _scale * 2))
        self.add_component(PhotoVoltaicBottomConnector(self.pos.x, self.pos.y + 13 * _scale * 2))
        self.add_component(PhotoVoltaicEdge(self.pos.x - _scale * offset, self.pos.y - 13 * _scale * 2))
        self.add_component(PhotoVoltaicEdge(self.pos.x + _scale * offset, self.pos.y - 13 * _scale * 2))
        self.add_component(PhotoVoltaicEdge(self.pos.x - _scale * offset, self.pos.y + 12 * _scale * 2))
        self.add_component(PhotoVoltaicEdge(self.pos.x + _scale * offset, self.pos.y + 12 * _scale * 2))
        # for i in range(-12 * 1, 12 * 1):
        #     self.add_component(
        #         PhotoVoltaicMidConnector(self.pos.x, self.pos.y + i * _scale * 2)
        #     )
        self.angle = angle


class SolarPanelSegment(SpriteComponent):
    def __init__(self, x, y):
        super().__init__(x, y, 'solar_panel_segment.png', _scale)


class Segment(SpriteComponent):
    def __init__(self, x, y):
        super().__init__(x, y, 'segment.png', _scale)


class HeatRejectionSubsystem(SpriteComponent):
    def __init__(self, x, y):
        super().__init__(x, y, 'heat_rejection_subsystem.png', _scale / 2)


class HeatRejectionSubsystemRadiator(SpaceComponent):
    def __init__(self, x, y):
        super().__init__(x, y)
        for i in range(-4, 4):
            self.components.append(HeatRejectionSubsystem(self.pos.x, self.pos.y + i * _scale / 2 * 6.5))


class Module(SpriteComponent):
    def __init__(self, x, y, scale=_scale):
        super().__init__(x, y, 'module.png', scale)


class ModuleSegment(SpriteComponent):
    def __init__(self, x, y, scale=_scale):
        super().__init__(x, y, 'module_segment.png', scale)


class PressurisedMatingAdaptor(SpriteComponent):
    def __init__(self, x, y, scale=_scale):
        super().__init__(x, y, 'pma.png', scale)


class ServiceModule(SpriteComponent):
    def __init__(self, x, y, scale=_scale):
        super().__init__(x, y, 'service_module.png', scale)


class LeftSegment(SpaceComponent):
    def __init__(self, x, y):
        super().__init__(x, y)
        offset = 5 * _scale
        w = 8 * _scale
        self.add_component(Segment(self.pos.x, self.pos.y))
        self.add_component(Segment(self.pos.x - w * 1, self.pos.y))
        self.add_component(Segment(self.pos.x - w * 2, self.pos.y))
        self.add_component(Segment(self.pos.x + w * 1, self.pos.y))
        self.add_component(PhotoVoltaicPanel(self.pos.x - w * 2 - offset, self.pos.y - 16 * _scale * 2))
        self.add_component(p1 := PhotoVoltaicPanel(self.pos.x - w * 2 - offset, self.pos.y + 16 * _scale * 2, 0))
        p1.rotate_by(180)
        self.add_component(PhotoVoltaicPanel(self.pos.x + offset / 2, self.pos.y - 16 * _scale * 2))
        self.add_component(p2 := PhotoVoltaicPanel(self.pos.x + offset / 2, self.pos.y + 16 * _scale * 2, 0))
        p2.rotate_by(180)


class RightSegment(SpaceComponent):
    def __init__(self, x, y):
        super().__init__(x, y)
        offset = 5 * _scale
        w = 8 * _scale
        self.add_component(Segment(self.pos.x, self.pos.y))
        self.add_component(Segment(self.pos.x + w * 1, self.pos.y))
        self.add_component(Segment(self.pos.x + w * 2, self.pos.y))
        self.add_component(Segment(self.pos.x - w * 1, self.pos.y))
        self.add_component(PhotoVoltaicPanel(self.pos.x + w * 2 + offset, self.pos.y - 16 * _scale * 2))
        self.add_component(p1 := PhotoVoltaicPanel(self.pos.x + w * 2 + offset, self.pos.y + 16 * _scale * 2, 0))
        p1.rotate_by(180)
        self.add_component(PhotoVoltaicPanel(self.pos.x - offset / 2, self.pos.y - 16 * _scale * 2))
        self.add_component(p2 := PhotoVoltaicPanel(self.pos.x - offset / 2, self.pos.y + 16 * _scale * 2, 0))
        p2.rotate_by(180)


class MiddleSegment(SpaceComponent):
    def __init__(self, x, y):
        super().__init__(x, y)
        offset = _scale * 30
        y_offset = _scale * 16
        self.add_component(HeatRejectionSubsystemRadiator(self.pos.x + offset, self.pos.y - y_offset))
        self.add_component(HeatRejectionSubsystemRadiator(self.pos.x - _scale / 2 * 10 + offset, self.pos.y - y_offset))
        self.add_component(HeatRejectionSubsystemRadiator(self.pos.x + _scale / 2 * 10 + offset, self.pos.y - y_offset))
        self.add_component(HeatRejectionSubsystemRadiator(self.pos.x - offset, self.pos.y - y_offset))
        self.add_component(HeatRejectionSubsystemRadiator(self.pos.x - _scale / 2 * 10 - offset, self.pos.y - y_offset))
        self.add_component(HeatRejectionSubsystemRadiator(self.pos.x + _scale / 2 * 10 - offset, self.pos.y - y_offset))

        self.add_component(Module(self.pos.x + 2 * 24, self.pos.y - y_offset * 0.6, 2))
        self.add_component(Module(self.pos.x, self.pos.y - y_offset * 0.62, 1.5).rotate_by(90))
        self.add_component(Module(self.pos.x, self.pos.y + y_offset / 2, 2).rotate_by(90))
        self.add_component(Module(self.pos.x, self.pos.y + y_offset * 1.5, 2).rotate_by(90))
        self.add_component(Module(self.pos.x - _scale * 13.5, self.pos.y + y_offset * 1.65, 2))
        self.add_component(ModuleSegment(self.pos.x + _scale * 18 - 2, self.pos.y + y_offset * 1.6, 3))

        self.add_component(ModuleSegment(self.pos.x, self.pos.y - y_offset * 1.8, 1.5).rotate_by(90))
        self.add_component(ModuleSegment(self.pos.x, self.pos.y - y_offset * 2.6 - 4, 2).rotate_by(90))

        self.add_component(PressurisedMatingAdaptor(self.pos.x, self.pos.y - y_offset * 1.2, 0.8))
        self.add_component(ServiceModule(self.pos.x, self.pos.y - y_offset * 3.7, _scale / 2))

        self.add_component(
            MiniPhotoVoltaicArray(self.pos.x + _scale * 13, self.pos.y - y_offset * 3.4, _scale / 2).rotate_by(90))
        self.add_component(
            MiniPhotoVoltaicArray(self.pos.x - _scale * 13, self.pos.y - y_offset * 3.4, _scale / 2).rotate_by(-90))

        w = 8 * _scale
        for i in range(-5, 6):
            self.add_component(Segment(self.pos.x + w * i, self.pos.y))

        self.add_component(Segment(self.pos.x - w * 1, self.pos.y - w))
        self.add_component(Segment(self.pos.x - w * 2, self.pos.y - w))


class SpaceStation(SpaceComponent):
    def __init__(self, x, y):
        super().__init__(x, y)
        offset = 56 * _scale
        self.add_component(LeftSegment(self.pos.x - offset, self.pos.y))
        self.add_component(RightSegment(self.pos.x + offset, self.pos.y))
        self.add_component(MiddleSegment(*self.pos))

    def update(self, events: list[pygame.event.Event], dt):
        super().update(events, dt)
        self.rotate_by(0.0 * dt)
