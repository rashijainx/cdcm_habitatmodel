

import os
import numpy as np
import itertools as it
from functools import partialmethod
from numbers import Number
from collections import defaultdict
from typing import Dict, Tuple, List

import matplotlib.pyplot as plt

from cdcm import *
from cdcm_abstractions import *
from cdcm_utils import *


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
    
    def plot_grid_with_labels(self, title="Grid Occupancy", directory="grid/", fname="grid_labels.png", show=True):
        fig, ax = plt.subplots()
        ax.set_xlim(0, self.nx)
        ax.set_ylim(0, self.ny)
        ax.set_xticks(np.arange(self.nx+1))
        ax.set_yticks(np.arange(self.ny+1))
        ax.grid(True)

        # assign each component a unique color
        colors = plt.cm.tab10.colors
        comp_to_color = {}

        for idx, component in enumerate({c for comps in self._grid.values() for c in comps}):
            comp_to_color[component] = colors[idx % len(colors)]

        # plot footprints
        for component, color in comp_to_color.items():
            # collect all cells this component occupies
            positions = [pos for pos, comps in self._grid.items() if component in comps]
            xs, ys = zip(*positions)

            # fill each occupied cell
            for (x, y) in positions:
                rect = plt.Rectangle((x, y), 1, 1, facecolor=color, alpha=0.3, edgecolor="black")
                ax.add_patch(rect)

            # compute bounding box center
            cx = (min(xs) + max(xs) + 1) / 2
            cy = (min(ys) + max(ys) + 1) / 2

            # label once in the center
            ax.text(cx, cy, component.absname, ha="center", va="center",
                    fontsize=8, fontweight="bold", color="black")

        ax.set_title(title)

        if not os.path.exists(directory):
            os.makedirs(directory)
        fpath = os.path.join(directory, fname)
        fig.savefig(fpath, dpi=300)
        if show:
            plt.show()

    

    # Simulation parameters

time_steps = 500

if __name__ == "__main__":

    with System(name="system") as system:

        clock = make_clock(dt=1.0, units="hours")

        dummy_component = make_component(
            name="dummy_component",
            aging_rate=0.01,
            dt=clock.dt,
            Ed=0.1,
        )

        another_dummy_component = make_component(
            name="another_dummy_component",
            aging_rate=0.02,
            dt=clock.dt,
            Ed=0.2,
        )

        grid = Grid(10, 10)

        dummy_component_positions = [(x, y) for x in range(2, 6) for y in range (1, 3)]
        another_dummy_component_positions = [(x, y) for x in range(5, 9) for y in range (7, 9)]
        grid.place_system(dummy_component, *dummy_component_positions)
        grid.place_system(another_dummy_component, *another_dummy_component_positions)


    file_name = __file__.split("/")[-1][:-3]

    system.forward()
    print(system)

    print(">.. Pyvis is making the HTML file.")

    tcs_graph = make_pyvis_graph(system)
    try:
        tcs_graph.show(file_name + ".html", notebook=False)
    except:
        tcs_graph.show(file_name + ".html")
    print(">... done")

    saver = SimulationSaver(
        file_name + ".h5",
        system,
        max_steps=time_steps,
        overwrite=True
    )
    model = Simulator(system)

    for i in range(time_steps):
        model.forward()
        saver.save()
        model.transition()

    grid.plot_grid(_t=0, _fig=True)
    grid.plot_grid_with_labels(title="Dummy Components Layout")

