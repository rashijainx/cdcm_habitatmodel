class Component:
    """
    Descripts any kind of component or collection thereof:
        Physical
        Software
        Electrical
        Thermal,
        etc
    """
    def __init__(self, name):
        self.name = name
        self.physical = None

class PhysicalComponent:
    """
    Physical Component has a Shape, Form, Position, and Material
    """
    def __init__(
        self,
        dimensions,
        shape,
        position=(0,0,0),
        material=None
    ):
        
        self.dimensions = dimensions
        self.shape = shape
        self.position = position
        self.material = material
