from src.engine.objects import AnimationStateObject
from src.engine.utils import get_path


class VFX(AnimationStateObject):
    def __init__(self, x, y, name, rows, cols, images, timer=0.1, scale=1, flip=(0, 0)):
        state_info = {
            'default': range(images)
        }
        super().__init__(get_path('images', 'vfx', f'{name}.png'), rows, cols, images, state_info, scale, timer)
        self.pos = x, y
        self.flip = flip
        self.run_once('default', self.destroy)
