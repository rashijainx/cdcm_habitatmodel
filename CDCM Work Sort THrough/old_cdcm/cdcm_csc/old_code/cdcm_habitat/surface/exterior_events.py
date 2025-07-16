"""Events external to the component models

Author:
    R Murali Krishnan
    
Date:
    10/04/2023
    
"""


__all__ = ["Meteorite", "make_meteorite_event"]


import numpy as np
from numbers import Number
from typing import NamedTuple, Tuple, Callable, List
from cdcm_constructs import event, Component
from cdcm_csc_systems import Grid


class Meteorite(NamedTuple):
    position: Tuple[int, int]
    t: Number
    E: Number


@event
def make_meteorite_damage_components(components: List[Component], impact_energy: Number):
    """An event that damages a component"""

    through_energy = impact_energy
    for component in [c for c in components if c.health.value > 0.0]:
        hv_new = component.impact_based_damage(through_energy)
        if hv_new <= 0:
            through_energy = max(impact_energy - component.Ed_star, 0.0)
            component.health.value = max(hv_new, 0.0)
            if through_energy > 0.0:
                continue
            else:
                break
        else:
            component.health.value = hv_new
            break

            

def make_meteorite_event(grid: Grid, meteorite: Meteorite) -> Callable:
    """Make a meteorite event"""
    if meteorite.position in grid.grid_points_with_components:
        # process and return an event
        components_in_grid = grid[meteorite.position]
        return make_meteorite_damage_components(components_in_grid, meteorite.E)
    else:
        return None