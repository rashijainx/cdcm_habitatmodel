from .node import Node


class Component(Node):
    """
    Descripts any kind of component or collection thereof:
        Physical
        Software
        Electrical
        Thermal,
        etc
    """
    def __init__(self, name, owner=None):
        super().__init__(name=name, owner=owner)
        self.physical = None

class PhysicalComponent(Component):
    """
    Physical Component has a Shape, Form, Position, and Material
    """
    def __init__(
        self,
        name,
        dimensions,
        shape,
        position=(0,0,0),
        material=None,
        **kwargs
    ):
        super().__init__(name=name, owner=None)

        self.dimensions = dimensions
        self.shape = shape
        self.position = position
        self.material = material
