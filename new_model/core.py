from common_functions import *

class PhysicalComponent:
    def __init__(
        self,
        name,
        length,
        width,
        height,
        material=None
    ):
        self.name = name
        self.length = length
        self.width = width
        self.height = height
        self.material = material

        # Volume
        @property
        def volume(self):
            return calculate_product(
                self.length,
                self.width,
                self.height
            )
