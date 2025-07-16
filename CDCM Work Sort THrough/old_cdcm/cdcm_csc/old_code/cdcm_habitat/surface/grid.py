"""Grid on which to place the components

Author:
    R Murali Krishnan
    
Date:
    10/04/2023
    
"""


import os
import numpy as np
import itertools as it
from functools import partialmethod
from numbers import Number
from collections import defaultdict
from typing import Dict, Tuple, List
from cdcm_constructs import Component
import matplotlib.pyplot as plt


class Grid():
    """Simple grid world for CDCM-based habitat models"""
    def __init__(self, nx, ny, *args, print_depth: Number=3, **kwargs) -> None:
        self.nx = nx
        self.ny = ny
        self.rangex = range(nx)
        self.rangey = range(ny)
        self.positions = list(it.product(self.rangex, self.rangey))
        self._grid: Dict[Tuple[int,int], List[Component]] = defaultdict(list)
        self._depth = print_depth


    def __setitem__(self, __key, __val):
        raise RuntimeError("Use the `place_component` method to assign component items to a grid")
    
    def __getitem__(self, grid_position: Tuple[int, int]) -> List[Component]:
        assert grid_position in self.positions
        return self._grid[grid_position]

    def place_system(self, component: Component, *positions) -> None:
        """Place a component in a position in the grid"""
        for pos in positions:
            assert pos in self.positions
            if component not in self._grid[pos]:
                self._grid[pos].append(component)
            else:
                raise RuntimeError(f"{component.absname} is already placed in the grid")
            

    @property
    def grid_points_with_components(self):
        return list(self._grid.keys())
            
    def __str__(self):
        """Outputs the grid positions occupied by the absolute name of components"""
        grid_size = len(self._grid)
        grid_str = "OccupancyGrid({\n"
        for ipos, (pos, components) in enumerate(self._grid.items()):
            grid_str += str(pos) + " : ["
            ncomponents = len(components)
            for icomp, component in enumerate(components):
                grid_str += '/'.join(component.absname.split("/")[-self._depth:])
                if icomp + 1 < ncomponents:
                    grid_str += ", "
            if ipos + 1 < grid_size:
                grid_str += "],\n"
            else:
                grid_str += "]"
        grid_str += "})"
        return grid_str
    
    def plot_grid(self, _t: Number, directory: str="grid/", _fig: bool=True):
        """Print the grid with average health values"""

        _grd = -1.0 * np.ones((self.nx, self.ny))
        # import pdb; pdb.set_trace()
        for pos, components in self._grid.items():
            ix, iy = pos
            hvals = [c.health.value for c in components]
            _grd[ix,iy] = sum(hvals) / len(hvals)

        if _fig:
            if not os.path.exists(directory):
                os.makedirs(directory)
            _file_name = directory + f"time={_t}.png"
            f, ax = plt.subplots()
            c = ax.pcolor(_grd.T, cmap='RdYlGn_r', vmin=0.0, vmax=1.0)
            ax.set_title(f"Health in the Grid @ time={_t} hours")
            f.tight_layout()
            f.colorbar(c, ax=ax)
            f.savefig(_file_name, dpi=300)
        return _grd
    