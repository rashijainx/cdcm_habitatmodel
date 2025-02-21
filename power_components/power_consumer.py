from cdcm import *
from cdcm_abstractions import *

from .switch import *
__all__ = ["make_power_consumer",
           "make_integrated_power_consumer"]

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
    clock: System,
    aging_rate: float,
    switch_aging_rates: tuple,
    fuse_voltage_in: Variable,
    power_consumer_spec: tuple,

) -> System:

    with System(name=name) as power_consumer:

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

        switch = make_integrated_switch(
            "switch",
            clock,
            switch_aging_rates,
            fuse_voltage_in,
            (power_consumer_spec[1], power_consumer_spec[2]),
        )

        power_consumer_functionality_inputs = [
            hardware,
            switch
        ]

        vacuum_functionality = make_functionality(
            *power_consumer_functionality_inputs,
            name=power_consumer_spec[0],
        )

   
    return power_consumer