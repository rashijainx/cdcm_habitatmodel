from cdcm import *
from cdcm_abstractions import *

__all__ = ["make_power_consumer"]

def make_power_consumer(
    name: str,
    clock: System,
    aging_rate: float,
    switch: System, 
) -> System:

    with System(name=name) as power_connsumer:

        hardware = make_component(
            name="hardware",
            health_damage_rate=aging_rate,
            dt=clock.dt,
            Ed=1.0
        )

        vaccum_functionality_inputs = [
            hardware,
            switch
        ]

        vacuum_functionality = make_functionality(
            *vaccum_functionality_inputs,
            name="vacuum_cleaner"
        )

   
    return power_connsumer