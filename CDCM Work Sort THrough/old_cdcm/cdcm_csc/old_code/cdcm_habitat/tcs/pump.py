""" Model of Pump in TCS

Author:
    Rashi Jain

Date:
    1/28/2024 | Initial Model
    3/22/2024 | Updated Model

    Is the pump able to regulate the fluid pressure?
"""

from cdcm import *
from cdcm_constructs import *

from .plumbing_assembly import make_plumbing_assembly

from typing import Optional

__all__ = ["make_pump"]

def make_pump(
    name: str, 
    clock: System,
    age_rate: float,
    interact_variable: float,
    mechanism_failure: float, 
    software_control: float,  # Abstraction
    power: float,  # Abstraction
    power_threshold: float,
    contamination_threshold: float,
    plumbing_age_rate: float,
    plumbing_interact_variable: float,
    plumbing_threshold_storage: float,
    plumbing_heat_transfer: float,
    valve_age_rate: float,
    valve_threshold: float,
    valve_interact_variable: float,
    valve_mechanism_failure: float,
    valve_control: float,
    plumbingIN: Optional[System[None]] = None,
    ) -> System:

    with System(name=name) as pump:

        age_rate = Variable(name="age_rate", value=age_rate)
        interact_variable = Variable(
            name="interact_variable",
            value=interact_variable
        )
        mechanism_failure = Variable(
            name="mechanism_failure",
            value=mechanism_failure
        )
        software_control = Variable(
            name="software_control",
            value=software_control
        )
        power = Variable(
            name="power",
            value=power
        )
        power_threshold = Parameter(
            name="power_threshold",
            value=power_threshold
        )
        contamination_threshold = Parameter(
            name="contamination_threshold",
            value=contamination_threshold
        )

        # HARDWARE
        hardware =  make_component(
            name = "hardware",
            dt= clock.dt,
            aging_rate=age_rate, 
            Ed = 1., 
        )

        hardware_functionality_inputs=(
            hardware,
            interact_variable,
            mechanism_failure,
            power,
            power_threshold,
            plumbingIN.coolant.contamination,
            contamination_threshold,
        )

        def fn_hardware(
            hardware,
            interact_variable,
            mechanism_failure,
            power,
            power_threshold,
            contamination,
            contamination_threshold,
        ) -> float:
            if power < power_threshold:
                x = 0 
            elif contamination > contamination_threshold:
                x = hardware*(1 - interact_variable)*\
                    (1 - mechanism_failure)*(1 - contamination \
                    + contamination_threshold)
            elif power < power_threshold and contamination > contamination_threshold: 
                x = hardware*(1 - interact_variable)*\
                (1 - mechanism_failure)*(1 - contamination \
                + contamination_threshold)
            else: 
                x = hardware*(1 - interact_variable)*\
                (1 - mechanism_failure)
            return x 

        hardware_functionality = make_functionality(
            name="hardware_functionality",
            *hardware_functionality_inputs,
            functionality_func = fn_hardware
        )

        pump_functionality_inputs=(
            software_control,
            hardware_functionality,
        )

        pump_functionality = make_functionality(
            *pump_functionality_inputs
        )

        plumbing = make_plumbing_assembly(
            "plumbing",
            "pump",
            clock,
            plumbing_age_rate,
            plumbing_interact_variable,
            plumbing_threshold_storage,
            plumbing_heat_transfer,
            valve_age_rate,
            valve_threshold,
            valve_interact_variable,
            valve_mechanism_failure,
            valve_control,
            plumbingIN,
            pump_functionality,
        )

    return pump
