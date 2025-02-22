from cdcm import *
from cdcm_abstractions import *

from common_constructs import *
from switch import *

__all__ = [
    "make_power_consumer",
    "make_integrated_power_consumer",
    "make_multiple_integrated_power_consumer",
]

def make_power_consumer(
    name: str,
    clock: System,
    aging_rate: float,
    switch: System, 
    function_name: str,
) -> System:

    with System(name=name) as power_consumer:

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
            name=function_name
        )

   
    return power_consumer

def make_integrated_power_consumer(
    name: str,
    function: str,
    clock: System,
    temperature: Variable,
    age_parameters: tuple,
    specifications: tuple,
    temperature_specs: tuple,
    switch_parameters: tuple,
    fuse_parameters: tuple,
    wiring_parameters: tuple,
    power_distributor: System,
) -> System:

    with System(name=name) as power_consumer:

        aging = make_aging_component(
            "aging",
            clock,
            age_parameters,
            (temperature_specs[0], temperature_specs[1]),
            (temperature_specs[2], temperature_specs[3]),
            temperature,
        )
        
        switch = make_integrated_switch(
            "switch", 
            clock,
            switch_parameters,
            fuse_parameters,
            wiring_parameters,
            specifications,
            power_distributor,
        )

        tolerance = Parameter(
            name="tolerance",
            value=age_parameters[2],
        )

        power_consumer_functionality_capability = (
            aging.hardware,
            tolerance,
        )

        def make_power_consumer_functionality_capability(
            hd=aging.hardware,
            tol=tolerance,
        ): 
            if hd > tol: 
                return hd
            else: 
                return 0.0

        consumer_functional_capability_name = function.split("_")[0]
        consumer_functionality = make_functionality(
            *power_consumer_functionality_capability,
            name=consumer_functional_capability_name + "_ability",
            functionality_func=make_power_consumer_functionality_capability
        )

        consumer_function_inputs = (
            consumer_functionality,
            switch.functionality,
        )

        consumer_function = make_functionality(
            *consumer_function_inputs,
            name=function,
        )

    return power_consumer


def make_multiple_integrated_power_consumer(
    name: str,
    function: str,
    clock: System,
    temperature: Variable,
    consumer_aging_parameters: tuple,
    consumer_parameters: tuple, 
    consumer_tempearture_specs: tuple,
    switch_aging_parameters: tuple,
    fuse_aging_parameters: tuple,
    wiring_aging_parameters: tuple,
    power_distributor: System,
) -> System:

    with System(name=name) as power_consumer:

        number_of_consumers = consumer_parameters[0]

        for i in range(number_of_consumers+1): 
            consumer = make_integrated_power_consumer(
                str(i), 
                function,
                clock,
                temperature,
                consumer_aging_parameters,
                consumer_parameters,
                consumer_tempearture_specs,
                switch_aging_parameters,
                fuse_aging_parameters,
                wiring_aging_parameters,
                power_distributor,
            )
   
    return power_consumer