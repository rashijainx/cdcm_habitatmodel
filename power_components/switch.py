from cdcm import *
from cdcm_abstractions import *

__all__ = ["make_switch",
           "make_fuse", 
           "make_integrated_switch"]


def make_fuse(
    name: str,
    clock: System,
    aging_rate: float,
    voltage_in: Variable,
    power_consumer: tuple, 
) -> System:

    with System(name=name) as switch:

        hardware = make_component(
            name="hardware",
            health_damage_rate=aging_rate,
            dt=clock.dt,
            Ed=1.0
        )

        status = Variable(
            name="status",
            value=1
        )

        consumer_operational_status = Variable(
            name="consumer_operational_status",
            value=power_consumer[0]
        )

        consumer_voltage_rating = Variable(
            name="consumer_voltage_rating",
            value=power_consumer[1]
        )

        @make_function(status)
        def calc_status(
            voltage=voltage_in,
            os = consumer_operational_status,
            consumer=consumer_voltage_rating,
        ):
            if os == 1: 
                if consumer > voltage: 
                    return 0
                else:
                    return 1
            else: 
                return 1
   
    return switch

def make_switch(
    name: str,
    clock: System,
    aging_rate: float,
    fuse: System,
) -> System:

    with System(name=name) as switch:

        hardware = make_component(
            name="hardware",
            health_damage_rate=aging_rate,
            dt=clock.dt,
            Ed=1.0
        )

        switch_functionality_inputs = [
            hardware,
            fuse.status,
        ]

        switch_functionality = make_functionality(
            *switch_functionality_inputs
        )
   
    return switch


def make_integrated_switch(
    name: str,
    clock: System,
    switch_aging_rate: float,
    fuse_aging_rate: float,
    fuse_voltage_in: Variable,
    power_consumer_spec: tuple, 
) -> System:

    with System(name=name) as switch:

        hardware = make_component(
            name="hardware",
            health_damage_rate=switch_aging_rate,
            dt=clock.dt,
            Ed=1.0
        )

        fuse = make_fuse(
            "fuse", 
            clock,
            fuse_aging_rate,
            fuse_voltage_in,
            power_consumer_spec
        )

        switch_functionality_inputs = [
            hardware,
            fuse.status,
        ]

        switch_functionality = make_functionality(
            *switch_functionality_inputs
        )
   
    return switch