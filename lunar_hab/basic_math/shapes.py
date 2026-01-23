import math

from .math_functions import *

class Shapes:
    """
    A container for all following shape definitions: 
        Box
        Sphere
        Cylinder
        Cone
        Torus
        Hexagonal Prism
    """
    class Box:
        def __init__(self, length, width, height):
            self.dims = (length, width, height)

            def volume(self):
                l, w, h = self.dims
                return calculate_product(l, w, h)

    class Sphere:
        def __init__(self, radius):
            self.dims = radius

            def volume(self):
                return (4/3) * math.pi * calculate_cube (self.radius)

    class Cylinder:
        def __init__(self, radius, height):
            self.dims = (radius, height)

            def volume(self):
                return math.pi * calculate_product(calculate_square(self.radius), self.height)
