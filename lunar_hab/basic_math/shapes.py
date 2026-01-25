import math

from .math_functions import *

class Shapes:
    """
    A container for all following shape definitions: 
        Box
        Sphere
        Cylinder
    """
    class Box:
        def __init__(self, length, width, height):
            self.length = length
            self.width = width
            self.height = height

        def volume(self):
            return calculate_product(self.length, self.width, self.height)

    class Sphere:
        def __init__(self, radius):
            self.radius = radius

        def volume(self):
            return calculate_product((4/3), math.pi, calculate_cube (self.radius))

    class Cylinder:
        def __init__(self, radius, height):
            self.radius = radius
            self.height = height

        def volume(self):
            return calculate_product(calculate_square(self.radius), self.height, math.pi)
