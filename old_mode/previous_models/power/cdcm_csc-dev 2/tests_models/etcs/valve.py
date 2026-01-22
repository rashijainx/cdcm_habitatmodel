""" Model of the valve 

Author: 
    Rashi Jain 

Date: 
    10/10/2023 

""" 

from cdcm import * 
from cdcm_csc import * 

__all__ = ["make_valve"] 

def make_valve( 
    instance_name: str,
    clock: System, 
    switch: System, 
    connector: System, # Input System flowing into the valve. 
    age_rate: NumOrVar, 
) -> System: 

    with System(name=instance_name) as valve:  

        hardware = make_component(
            name="hardware",
            dt=clock.dt, 
            aging_rate=age_rate, 
            Ed=1.0, 
        )

        # This has to be worked around a little bit. 
        clog = make_component(
            name="clog", 
            health=connector.contamination.health,
        )

        agent_mishandling = make_component(name="agent_mishandling", units=1.0)

        valve_functionality_inputs = ( 
            switch, 
            hardware, 
            clog, 
            agent_mishandling, 
        )

        valve_functionality = make_functionality(*valve_functionality_inputs)

    return valve

