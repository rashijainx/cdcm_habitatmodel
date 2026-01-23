from lunar_hab.basic_math import *

class PhysicalComponent:
    """
    Physical Component has a Name, Position, Shape & Dimensions, Material
    """
    def __init__(
        self,
        name,
        position,
        shape,
        dimensions,
        material=None
    ):
        self.name = name
        self.position = position
        self.shape = shape
        self.dimensions = dimensions
        self.material = material

