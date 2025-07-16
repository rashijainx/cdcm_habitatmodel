from cdcm import *
from cdcm_abstractions import *

__all__ = ["make_wiring",]


def make_wiring(
    name: str,
    clock: System,
    wiring_aging_parameters: tuple,
) -> System:

    with System(name=name) as wiring:

        age_rate = Variable(
            name="age_rate",
            value=wiring_aging_parameters[0]
        )
    
        hardware = make_component(
            name="hardware",
            health_damage_rate=age_rate,
            dt=clock.dt,
            Ed=1.0
        )

        threshold = Variable(
            name="threshold",
            value=wiring_aging_parameters[1]
        )
    
        functionality_inputs = [
            hardware,
            threshold
        ]

        def make_wiring_functionality(
                hw = hardware, 
                th = threshold, 
        ): 
            if hw < th: 
                return 0.0
            else: 
                return 1.0

        functionality = make_functionality(
            *functionality_inputs,
            name="transfer_electricity", 
            functionality_func=make_wiring_functionality
        )
   
    return wiring

