from src.engine.objects import BaseObject


class Component(BaseObject):
    def __init__(self, x, y, destroy_components=True):
        super().__init__(x, y)
        self.destroy_components = destroy_components  # if this is destroyed, then components too or not
        self.parent: Component | None = None
        self.components: list[BaseObject] = []
        self.angle = 0
        self.scale = 1

    def rotate_by(self, angle):
        self.angle += angle
        for i in self.components:
            i.pos = self.pos + (i.pos - self.pos).rotate(angle)
            if isinstance(i, Component):
                i.rotate_by(angle)
        return self

    def on_ready(self):
        self.object_manager.add_multiple(self.components)

    def move(self, dx, dy):
        for i in self.components:
            i.move(dx, dy)
        super().move(dx, dy)

    def add_component(self, component: BaseObject):
        self.components.append(component)
        if isinstance(component, Component):
            component.parent = self

    def remove_component(self, component: BaseObject):
        self.components.remove(component)
        if isinstance(component, Component):
            component.parent = None

    def destroy(self):
        if self.destroy_components:
            for i in self.components:
                i.destroy()
        super().destroy()
