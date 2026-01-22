"""Safety-controls for the CSC Scenario

Author:
    R Murali Krishnan
    
Date:
    09.22.2023
    
"""

from cdcm import *
from cdcm_constructs import *

from pdb import set_trace as keyboard
from numbers import Number

from .inventory import *


@event
def maintain(component: Component, 
             inventory: Inventory, 
             replacement_threshold: Number,
             maintenance_coeff: Number=1.1,
             debug: bool=False,
             **kwargs):
    """A maintenance event
    
    Arguments:
    ----------
    component               :   Component
        Component system which is being maintained
    inventory               :   Inventory
        Inventory system which logs the change in consumables
    replacement_threshold   :   Number
        Threshold which determines the switch of the repair v/s replace policy
    maintenance_coeff       :   Number (default = 1.1)
        Maintenance coefficient for increasing the health state of the component
    debug                   :   bool (default = False)
        Print debug infomation
    """

    # How much "repair" can happen to the component?
    hv = component.health.value
    hv_nominal = component.nominal_health

    if hv < replacement_threshold:
        # perform replacement
        hv_new = perform_component_replacement(component, inventory)
    elif hv > replacement_threshold and hv < hv_nominal:
        # perform repair
        hv_new = perform_component_repair(component, inventory, maintenance_coeff)
    else:
        # don't do anything
        hv_new = hv

    if debug:
        simulator: Simulator = kwargs.get("simulator")
        msg = (f"At [{simulator._system.clock.t.value} hrs]\n",
            f"Maintenance safety-control of << {component.name} >> is active\n",
            f"Current health: {hv:0.4f} / {hv_nominal:0.4f}, new health : {hv_new:0.4f}\n")
        
        print(*msg)       

    component.health.value = hv_new


def perform_component_repair(component: Component, 
                             inventory: Inventory, 
                             maintenance_coeff: Number):
    """Perform a component repair safety control"""
    hv = component.health.value
    hv_nominal = component.nominal_health
    tools_to_repair = component.tools_to_repair
    consumables_to_repair = component.consumables_to_repair

    # Check if we have the 'tools' and 'consumables' required to perform
    # the repair safety control
    has_tools = all([inventory.has_tool(item_id=tool, minimum_qty=qty) for tool, qty in tools_to_repair])
    has_consumables = all([inventory.has_consumable(item_id=consumable, minimum_qty=qty) for consumable, qty in consumables_to_repair])
    if has_tools and has_consumables:
        # Reduce consumables from the inventory
        for c, qty in consumables_to_repair:
            inventory.reduce_consumables(item_id=c, reduce_by=qty)
        
        # Update the component health state
        hv_new = min(hv * maintenance_coeff, hv_nominal)
    else:
        hv_new = hv

    return hv_new


def perform_component_replacement(component: Component, inventory: Inventory):
    """Perform a component repair safety control"""

    hv = component.health.value
    hv_nominal = component.nominal_health
    tools_to_replace = component.tools_to_replace
    consumables_to_replace = component.consumables_to_replace

    # Check if we have the 'tools' and 'consumables' required to perform
    # the LRU replacement safety control
    has_tools = all([inventory.has_tool(item_id=tool, minimum_qty=qty) for tool, qty in tools_to_replace])
    has_consumables = all([inventory.has_consumable(item_id=consumable, minimum_qty=qty) for consumable, qty in consumables_to_replace])
    if has_tools and has_consumables:
        # Reduce consumables from the inventory
        for c, qty in consumables_to_replace:
            inventory.reduce_consumables(item_id=c, reduce_by=qty)
        
        # Update the component health state
        hv_new = hv_nominal
    else:
        hv_new = hv

    return hv_new