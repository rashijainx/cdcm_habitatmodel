"""Model of an inventory system

Author:
    R Murali Krishnan
    
Date:
    09.14.2023
    
"""

import os
from typing import Dict, Union, Any
from numbers import Number
from functools import partialmethod
from pdb import set_trace as keyboard

from cdcm import *
from cdcm_constructs import *


class Inventory(System):
    """A class that describes the inventory system


    Arguments:
    ----------
    tools (Dict[str, Number])
    """


    def __init__(
        self,
        name: str,
        tools: Union[str, Dict[str, Any]],
        consumables: Union[str, Dict[str, Any]],
        **kwargs) -> None:
        # import pdb; pdb.set_trace()
        self.tools = tools
        self.consumables = consumables
        super().__init__(name=name, **kwargs)

    def _get_qty(self, 
                 item_id: str,
                 type_of_item: str,
                 qty_attr: str):
        return getattr(self, type_of_item)[item_id][qty_attr]
    
    tool_qty = partialmethod(_get_qty, type_of_item="tools", qty_attr="spares")
    consumable_qty = partialmethod(_get_qty, type_of_item="consumables", qty_attr="units")
    

    def _has_item(
        self, 
        type_of_item: str, 
        attr: str, 
        item_id: str, 
        minimum_qty: Number = 1.0) -> bool:
        """Checks if the `Inventory` has the item identified by the `item_id`"""
        item_lookup = getattr(self, type_of_item)
        return item_id in item_lookup and item_lookup[item_id][attr] >= minimum_qty

    has_tool = partialmethod(_has_item, type_of_item="tools", attr="spares")
    has_consumable = partialmethod(_has_item, type_of_item="consumables", attr="units")

    def _reduce_item(
        self, 
        type_of_item: str, 
        attr: str, 
        item_id: str, 
        reduce_by: Number = 1.0) -> None:
        """Reduce the number of items of either `tools` or `consumables` in the Inventory"""
        item_lookup = getattr(self, type_of_item)
        if item_lookup[item_id][attr] - reduce_by < 0:
            raise RuntimeError("Inventory items cannot have a negative value")
        else:
            item_lookup[item_id][attr] -= reduce_by

    reduce_tool = partialmethod(_reduce_item, "tools", "spares")
    reduce_consumables = partialmethod(_reduce_item, "consumables", "units")




def make_inventory(name: str = "inventory",
                   tool_file_path: str=None, 
                   consumables_file_path: str=None, 
                   **kwargs) -> Inventory:
    """Constuctor procedure for an inventory system"""

    # Parse tools stored in the inventory
    assert tool_file_path is not None and os.path.isfile(tool_file_path)
    tools = parse_yaml(tool_file_path)

    # Parse consumables stored in the inventory
    assert consumables_file_path is not None and os.path.isfile(consumables_file_path)
    consumables = parse_yaml(consumables_file_path)
    return Inventory(name=name, tools=tools, consumables=consumables)