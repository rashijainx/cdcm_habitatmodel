"""Model of a cold plate in ETCS

Author: 
    Darin Lin
    Rashi Jain

Date: 
    10/2/2023 - Developed the code. 
    10/2/2023 - Cleared up some concepts
    10/6/2023 - Integrated with Murali's format. 

"""
__all__ = ["make_cold_plate"]

from cdcm import *
from cdcm_csc import *

def make_cold_plate(
    clock: System,
    age_rate: NumOrVar,
    external_meteorite_impact: NumOrVar,
    plumbing: System,
    ) -> System:

    with System(name="cold_plate") as cold_plate:
        
        # EXTERNAL HARDWARE
        hardware = make_component(
            name="hardware",
            dt=clock.dt,
            aging_rate=age_rate,
            Ed = 10.0, 
        )

        agent_mishandling = make_component(name="agent_mishandling", nominal_health=1.0)

        cold_plate_functionality_inputs = (
            hardware, 
            agent_mishandling, 
            plumbing
        )

        cold_plate_functionality = make_functionality(*cold_plate_functionality_inputs)

    return cold_plate