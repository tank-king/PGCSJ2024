import pygame

from src.engine.objects import *
from src.engine.video import *
from src.objects.bullet import Bullet
from src.engine.sounds import SoundManager
from src.objects.space_station import SpriteComponent


# from src.objects.ship import Ship


class Player(BaseObject):
    def __init__(self, x, y):
        super().__init__(x, y, True)
        self.z = LAYERS.PLAYER_LAYER
        self.img: Image | None = None
        self.gun_img: Image | None = None
        self.vel = pygame.Vector2()
        self.angular_vel = 0
        self.angle = -90

        self.gun_scale = ValueAnimator(1)
        self.ship_scale = ValueAnimator(1)

        self.mode = 'explore'

        # pygame.key.set_repeat(100, 50)
        self.bullet_timer = TimerObject(0.2, self.shoot)
        # self.laser = Laser(*self.pos)

    @property
    def camera(self):
        return self.object_manager.camera

    # def on_ready(self):
    #     self.object_manager.add(self.laser)

    def on_renderer_ready(self, renderer: Renderer):
        img = renderer.load_image(get_path('images', 'ships', 'spaceship.png'))
        self.img = Image(img, img.get_rect())
        img = renderer.load_image(get_path('images', 'ships', 'spaceship_guns.png'))
        self.gun_img = Image(img, img.get_rect())

    def shoot(self):
        if self.mode != 'shoot':
            return
        self.gun_scale.reset()
        self.ship_scale.reset()
        offset = 0.1
        self.gun_scale.set(1).lerp(1 - offset).lerp(1 + offset).lerp(1)
        offset = 0.05
        self.ship_scale.set(1).lerp(1 - offset).lerp(1 + offset).lerp(1)
        offsets = [
            [0, 11], [0, -11]
        ]
        for i in offsets:
            pos = self.pos + pygame.Vector2(*i).rotate(self.angle)
            self.object_manager.add(
                Bullet(
                    *pos, self.angle
                )
            )
        SoundManager.play('shoot')
        self.camera.camera_shake(1)
        # self.object_manager.add(
        #     VFX(self.x, self.y - 50, 'sheet', 2, 8, 14, 1 / 24, 1)
        # )

    def smartbomb(self):
        for i in self.object_manager.get_objects(SpriteComponent):
            if isinstance(i, SpriteComponent):
                i.get_damage(1)

    def update(self, events: list[pygame.event.Event], dt):
        # if self.mode == 'explore':
        #     self.camera.set_zoom(1)
        # else:
        #     self.camera.set_zoom(2)
        # self.camera.set_zoom(2.5 - self.vel.magnitude() / 8)
        self.bullet_timer.update(events, dt)
        self.gun_scale.update(events, dt)
        self.ship_scale.update(events, dt)
        keys = pygame.key.get_pressed()
        speed = 0.3 * dt
        dx = math.cos(math.radians(self.angle)) * speed * dt
        dy = math.sin(math.radians(self.angle)) * speed * dt

        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_z:
                    self.mode = 'shoot'
                    self.shoot()
                    self.bullet_timer.reset()
                if e.key == pygame.K_x:
                    self.smartbomb()
            if e.type == pygame.KEYUP:
                if e.key == pygame.K_z:
                    self.mode = 'explore'
        k = 1
        if keys[pygame.K_UP]:
            # self.mode = 'explore'
            self.vel += [dx, dy]
        if keys[pygame.K_DOWN]:
            k = -1
            # self.mode = 'explore'
            self.vel -= [dx, dy]
        angular_speed = speed * k
        if keys[pygame.K_LEFT]:
            self.angular_vel -= angular_speed
        if keys[pygame.K_RIGHT]:
            self.angular_vel += angular_speed
        self.vel.clamp_magnitude(1 * dt)
        self.vel *= 0.92 ** dt
        self.angular_vel = clamp(self.angular_vel, -3, 3)
        self.angular_vel *= 0.9 ** dt
        self.pos += self.vel
        offset = 400
        self.x = clamp(self.x, -offset, Config.WIDTH + offset)
        self.y = clamp(self.y, -offset, Config.HEIGHT + offset)
        self.angle += self.angular_vel * dt

        # self.laser.angle = self.angle
        # self.laser.pos = self.pos

    def render(self, renderer: Renderer, offset, scale=1.0, angle=0.0):
        self.gun_img.render(*(self.pos + offset), self.angle + angle, scale * self.gun_scale.value)
        self.img.render(*(self.pos + offset), self.angle + angle, scale * self.ship_scale.value)
