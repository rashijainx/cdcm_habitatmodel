from cdcm import *
from cdcm_abstractions import *

from wiring import * 

__all__ = [
    "make_fuse", 
    "make_integrated_switch"
]


def make_fuse(
    name: str,
    clock: System,
    aging_rates: tuple,
    consumer_specifications: tuple,
    power_distributor: System,
) -> System:

    with System(name=name) as fuse:

        age_rate = Variable(
            name="age_rate",
            value=aging_rates[0]
        )
    
        hardware = make_component(
            name="hardware",
            health_damage_rate=age_rate,
            dt=clock.dt,
            Ed=1.0
        )

        tolerance = Variable(
            name="tolerance",
            value=aging_rates[1]
        )
    
        functionality_inputs = [
            hardware,
            tolerance
        ]

        def make_fuse_functionality(
                hw = hardware, 
                tol = tolerance, 
        ): 
            if hw < tol: 
                return 0.0
            else: 
                return 1.0

        functionality = make_functionality(
            *functionality_inputs,
            name="protect equipment", 
            functionality_func=make_fuse_functionality
        )

        status = Variable(
            name="status",
            value=1.0,
        )

        consumer_operational_status = Parameter(
            name="consumer_operational_status",
            value=consumer_specifications[1],
        )

        consumer_voltage = Parameter(
            name="consumer_voltage",
            value=consumer_specifications[3],
        )

        @make_function(status)
        def calc_status(
            f = functionality,
            cos = consumer_operational_status,
            cv = consumer_voltage,
            iv = power_distributor.voltage,
        ):
            if cos == 1: 
                if iv > cv or f == 0:
                    return 0
                else:
                    return 1
            else: 
                return 1
   
    return fuse

def make_integrated_switch(
    name: str,
    clock: System,
    aging_rates: tuple,
    fuse_parameters: tuple,
    wiring_parameters: tuple,
    consumer_specifications: tuple,
    power_distributor: System, 
) -> System:
    with System(name=name) as switch:

        age_rate = Variable(
            name="age_rate",
            value=aging_rates[0]
        )
    
        hardware = make_component(
            name="hardware",
            health_damage_rate=age_rate,
            dt=clock.dt,
            Ed=1.0
        )

        tolerance = Variable(
            name="tolerance",
            value=aging_rates[1]
        )

        wiring = make_wiring(
            "wiring", 
            clock, 
            wiring_parameters
        )

        fuse = make_fuse(
            "fuse", 
            clock,
            fuse_parameters,
            consumer_specifications,
            power_distributor,
        )

        switch_functionality_inputs = (
            hardware,
            tolerance,
            fuse.status,
            wiring.transfer_electricity,
        )

        def make_switch_functionality(
            hd=hardware,
            tol=tolerance,
            fs=fuse.status,
            w=wiring.transfer_electricity,
        ): 
            if hd > tol and fs == 1.0 and w == 1.0: 
                return 1.0
            else: 
                return 0.0

        switch_functionality = make_functionality(
            *switch_functionality_inputs,
            functionality_func = make_switch_functionality
        )
   
    return switch