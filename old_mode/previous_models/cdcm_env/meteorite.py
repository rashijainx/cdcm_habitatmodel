"""Model of meteorites

Author:
    Murali Krishnan R
    
Date:
    10.31.2022
    
"""


__all__ = ["add_meteorite_shower_event", "change_omega_to"]


from tracemalloc import start
from cdcm import *
from typing import Union



def change_omega_to(new_value: Union[int, float], node: Union[Variable, System], attr: str=None):
    def event(*args, **kwargs):
        print(f"** Event (change_omega_to({new_value:1.2f})) **")
        if isinstance(node, Variable):
            node.value = new_value
        else:
            assert attr is not None
            _change_node = getattr(node, attr)
            _change_node.value = new_value
    return event

def add_meteorite_shower_event(simulator: Simulator, node: Variable, start_time: float, end_time: float):

    # Add a meteorite shower event (start time to end time)
    simulator.add_event(start_time, change_omega_to(1, node))
    simulator.add_event(end_time, change_omega_to(0, node))

    pass