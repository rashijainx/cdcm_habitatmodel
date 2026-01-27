__all__ = ["make_pyvis_graph"]

import pyvis.network as nt
import seaborn as sns
import itertools as it
from .system import System

# Define visual attributes for different node types
node_attrs = {
    "Variable":  {"shape": "dot", "size": 10},
    "State":     {"shape": "diamond", "size": 15}, # Distinct shape for State
    "Parameter": {"shape": "square", "size": 10},  # Distinct shape for Constants
    "Function":  {"shape": "triangle", "size": 20},
    "Transition": {"shape": "triangleDown", "size": 20},
    "Component": {"shape": "box", "size": 25},     # Visualization for the container itself
}

def get_node_style(type_name):
    """
    Returns the style dictionary for pyvis.
    """
    for key, val in node_attrs.items():
        if key in type_name:
            return val
    return {"shape": "dot"} # Default fallback

def make_pyvis_graph(sys: System, filename='system_graph.html') -> nt.Network:
    """Make a `pyviz` graph instance of the system"""

    # 'hierarchical' layout often works better for Systems Engineering trees,
    # but 'directed' is good for data flow.
    g = nt.Network(height='750px', width='100%', directed=True)

    # Use a high contrast palette
    cmap = it.cycle(sns.color_palette('bright').as_hex())
    
    colors = {}
    
    # Because sys.nodes is a SET, the order isn't guaranteed. 
    # Converting to sorted list helps keep colors consistent between runs.
    all_nodes = sorted(list(sys.nodes), key=lambda x: x.absname)

    for n in all_nodes:
        # Determine Color based on Owner (The "System" context)
        owner_name = n.owner.absname if n.owner else "Root"
        
        if owner_name not in colors:
            colors[owner_name] = next(cmap)

        ntype = type(n).__name__
        style = get_node_style(ntype)

        # Add the Node
        # title=... gives you a hover tooltip with description/units!
        g.add_node(
            n.absname, 
            label=n.name,  # Use short name for label to reduce clutter
            title=f"{ntype}: {n.description} ({getattr(n, 'units', '')})",
            color=colors[owner_name], 
            **style
        )

        # Add Edges (Data Flow)
        for c in n.children:
            g.add_edge(n.absname, c.absname)
            
    # Add Physics controls so you can untangle the graph manually
    g.show_buttons(filter_=['physics']) 
    return g