from cdcm import *
from cdcm_abstractions import *

__all__ = ["make_wiring", 
           "make_connection_wiring"]


def make_wiring(
    name: str,
    clock: System,
    aging_rate: float,
    threshold: float, 
) -> System:

    with System(name=name) as wiring:

        age_rate = Variable(
            name="age_rate",
            value=aging_rate
        )
    
        hardware = make_component(
            name="hardware",
            health_damage_rate=age_rate,
            dt=clock.dt,
            Ed=1.0
        )

        threshold = Variable(
            name="threshold",
            value=threshold
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
                return 0 
            else: 
                return 1

        functionality = make_functionality(
            *functionality_inputs,
            name="transfer_electricity", 
            functionality_func=make_wiring_functionality
        )
   
    return wiring


def make_connection_wiring(
    name: str,
    clock: System,
    aging_rate: float,
    wiring_threshold: tuple,
    connection: System,  
) -> System:

    with System(name=name) as wiring:

        age_rate = Variable(
            name="age_rate",
            value=aging_rate
        )
    
        hardware = make_component(
            name="hardware",
            health_damage_rate=age_rate,
            dt=clock.dt,
            Ed=1.0
        )

        threshold = Variable(
            name="threshold",
            value=wiring_threshold[0]
        )

        voltage_threshold = Variable(
            name="voltage_threshold",
            value=wiring_threshold[1]
        )
    
        functionality_inputs = [
            hardware,
            threshold
        ]

        def make_wiring_functionality(
                hw = hardware, 
                th = threshold, 
                v_th = voltage_threshold, 
                v = connection.voltage,
        ): 
            if hw < th and v_th > v: 
                return 1
            else: 
                return 0

        functionality = make_functionality(
            *functionality_inputs,
            name="transfer_electricity", 
            functionality_func=make_wiring_functionality
        )
   
    return wiring

