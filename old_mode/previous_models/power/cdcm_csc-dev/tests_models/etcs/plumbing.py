"""Model of a plumbing 

Author: 
    Rashi Jain
    Darin Lin 
    Noah Colasanti 

Date: 
    10/6/2023 - Integrated with Murali's format. 

"""


from cdcm import *
from cdcm_csc import *

from typing import Optional

__all__ = ["make_plumbing"]

def make_plumbing(
    instance_name: str, 
    clock: System,
    age_rate: NumOrVar,
    external_dust_rate: NumOrVar,
    external_meteorite_impact: NumOrVar,
    contamination_rate: NumOrVar=0.0,
    sysIN: Optional[System] = None, 
    ) -> System:

    with System(name=instance_name) as plumbing:
        
        # EXTERNAL HARDWARE
        hardware = make_component(
            name="hardware",
            dt=clock.dt,
            aging_rate=age_rate,
            Ed = 5.0, 
        )
        
        # Plumbing can be contaminated with dust only when meteorite impacts + valveIN/plumbingIN 
        
        contamination = make_component(
            name="contamination",
            dt=clock.dt,
            health_damage_rate=contamination_rate,
        )

        agent_mishandling = make_component(name="agent_mishandling", nominal_health=1.0)

        plumbing_functionality_inputs = [hardware, contamination, agent_mishandling]
        if sysIN is not None:
            plumbing_functionality_inputs.append(sysIN)

        plumbing_functionality = make_functionality(*plumbing_functionality_inputs) 

    return plumbing