"""Model of a switch 

Author: 
    Rashi Jain 

Date: 
    09/10/2023

"""


from cdcm import *
from cdcm_csc import *

__all__ = ["make_switch"]

def make_switch(
        instance_name: str,
        clock: System,
        age_rate: NumOrVar,
    ) -> System:

    with System(name=instance_name) as switch:

        # External Inputs
        power = make_component(name="power", nominal_health=1,)

        # Present in software-supported switches 
        # SOFTWARE (also affected by Power and Sensor)
        # Algorithm -> Continous (Erratic) / Non-continous (Algorithm Update)
        human_updates_algorithm = make_component(
            name="human_updates_algorithm", nominal_health=1,
        )

        # Have bits of binary switch flips for eccentric behavior time period. 
        # eccentric_behavior_algorithm = make_component(
        #     name="eccentric_behavior_algorithm",
        #     clock=clock,
        #     health_damage_rate=eccentric_amplitude,
        # )

        # HARDWARE (age) - also affected by power
        # Replace when functionality if below a threshold
        # Maybe when Ed = 1.0 have the switch in the position such that it stays in the position it is in. 
        hardware = make_component(
            name="hardware",
            dt=clock.dt,
            aging_rate=age_rate,
            Ed=1.0,
        )
    
        # Parameter defined by outer parameters.
        agent_action = make_component(name="agent_action", nominal_health=1)

        switch_functionality_inputs = (
            power,
            human_updates_algorithm,
            hardware,
            agent_action,
        )

        switch_functionality = make_functionality(*switch_functionality_inputs)

    return switch


