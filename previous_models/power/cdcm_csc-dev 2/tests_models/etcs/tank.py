"""Model of a tank in ETCS

Author: 
    Darin Lin
    Rashi Jain

Date: 
    10/2/2023
    10/9/2023 - Integrated iwth Murali's model. 

"""

from cdcm import *
from cdcm_csc import *

def make_tank(
    clock: System,
    tank_age_rate: NumOrVar,
    external_dust_rate: NumOrVar, 
    external_meteorite_impact: NumOrVar, 
    valveIN: System, # Would come into picture as we talk about fluid quantity and quality 
) -> System:
    
    with System(name="tank") as tank:
        
        # EXTERNAL HARDWARE
        hardware = make_component(
            name="hardware",
            dt=clock.dt,
            aging_rate=tank_age_rate,
            Ed=70.0, 
        )
 
        # only related to disruptions on the tank + valveIN 
        contamination = make_component(
            name="contamination", 
            dt=clock.dt, 
            health_damage_rate=0.0, 
        )

        functionality_inputs = (
            hardware,
            contamination,
        )

        # FLUID QUALITY OUT OF TANK 
        functionality = make_functionality(
            *functionality_inputs,
        )

    return tank