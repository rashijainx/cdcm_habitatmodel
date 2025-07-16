"""Date visualization utilities

Author:
    R Murali Krishnan

Date:
    09.15.2023

"""


__all__ = ["parse_yaml", "make_pyvis_graph"]

import os
import yaml
from cdcm import *
import numpy.typing as npt
from typing import Dict, Any
import pyvis
import pyvis.network as nt
import seaborn as sns
import itertools as it


def get_simulation_data(
    saver: SimulationSaver, name2handle: Dict[str, str]
) -> Dict[str, npt.NDArray]:
    """Extract data from a `SimulationSaver`"""
    named_data = {}
    for name, handle in name2handle.items():
        try:
            named_data[name] = saver.file_handler[handle][:]
        except:
            import pdb

            pdb.set_trace()
    return named_data


def parse_yaml(filepath, **kwargs) -> Dict[str, Dict[str, Any]]:
    """Parse YAML files and return content as a dict of dicts"""
    with open(filepath, "r") as f:
        filecontents = yaml.safe_load_all(f)
        parsed_content = [content for content in filecontents]
    return parsed_content[0] if len(parsed_content) == 1 else parsed_content


node_shapes = {
    "Function": {"shape": "triangle"},
    "Transition": {"shape": "triangle"},
    "Test": {"shape": "ellipse"},
    "HealthState": {"shape": "square"},
    "Variable": {"shape": "dot"},
    "State": {"shape": "dot"},
    "Parameter":{"shape": "dot"}
}

def find_closest_key(type_name):
    """Find the key from node_shapes matching the type_name"""
    for key, val in node_shapes.items():
        if key in type_name:
            return {key: val}


def make_pyvis_graph(sys: System) -> nt.Network:
    """Make a `pyviz` graph instance of the system"""

    g = nt.Network('1500px', '75%', directed=True)

    cmap = it.cycle(sns.color_palette('pastel').as_hex())
    colors = {}
    for n in sys.nodes:
        owner_name = n.owner.absname
        ntype = type(n).__name__
        if owner_name not in colors:
            colors[owner_name] = next(cmap)

        g.add_node(n.absname, label=n.absname, color=colors[owner_name], **find_closest_key(ntype))
        for c in n.children:
            ctype = type(c).__name__
            g.add_node(c.absname, label=c.absname, color=colors[owner_name], **find_closest_key(ctype))
            g.add_edge(n.absname, c.absname)
    g.show_buttons()
    g.set_edge_smooth('dynamic')
    return g
