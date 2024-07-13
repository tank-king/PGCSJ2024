from src.objects.vfx import VFX
from src.engine.sounds import SoundManager

class Explosion(VFX):
    def __init__(self, x, y, scale=1):
        super().__init__(x, y, 'sheet', 2, 8, 14, 1 / 24, scale)

    def on_ready(self):
        SoundManager.play('explosion')


class Spark(VFX):
    def __init__(self, x, y, scale=1):
        super().__init__(x, y, 'spark_smooth', 1, 9, 9, 1 / 24, scale / 8)

    def on_ready(self):
        SoundManager.play('spark')
