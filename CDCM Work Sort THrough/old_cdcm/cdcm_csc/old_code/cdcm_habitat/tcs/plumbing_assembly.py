"""Plumbing with an out-valve and the coolant within it

Author:
    Rashi Jain

Date:
    02.15.2024
    02.21.2024 | Pep-8

"""

from cdcm import *
from cdcm_constructs import *

from .valve import make_valve
from .coolant import make_coolant

from typing import Optional

__all__ = ["make_plumbing_assembly"]

def make_plumbing_assembly(
    name: str,
    type: str, # "standard", "heatIN", "heatOUT", "pump"
    clock: System,
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
    affect: Optional[Variable] = None,
) -> System: 

    with System(name=name) as plumbing_assembly:

        # Valve
        valve = make_valve(
            "valve",
            clock,
            valve_age_rate,
            valve_threshold,
            valve_interact_variable,
            valve_mechanism_failure,
            valve_control,
        )

        # HARDWARE
        age_rate = Variable(name="age_rate", value=plumbing_age_rate)
        interact_variable = Variable(
            name="interact_variable",
            value=plumbing_interact_variable
            )
        threshold = Variable(
            name="threshold",
            value=plumbing_threshold_storage
            )
        heat_transfer_coeff = Variable(
            name="heat_transfer_coeff",
            value=plumbing_heat_transfer
        )

        hardware = make_component(
            name="hardware",
            dt=clock.dt,
            aging_rate=age_rate,
            Ed=1.0,
        )

        contain_fluid_inputs = (
            hardware,
            interact_variable,
            threshold,
        )

        def fn_contain_fluid(
                hardware,
                interact_variable,
                threshold
        ) -> float:
            if hardware < threshold:
                x = (hardware + (1 - threshold))*(1 - interact_variable)
            else:
                x = 1 - interact_variable
            return x

        contain_functionality = make_functionality(
            name="contain_fluid",
            *contain_fluid_inputs,
            functionality_func=fn_contain_fluid
        )

        insulate_heat_inputs = (
            hardware,
            threshold,
            interact_variable,
            heat_transfer_coeff,
        )

        def fn_insulate_heat(
                hardware,
                threshold,
                interact_variable,
                transfer_coeff) -> float:
            if hardware < threshold:
                x = (hardware + (1 - threshold)) * \
                    (1 - interact_variable) * \
                    (1 - transfer_coeff)
            else: 
                x = (1 - interact_variable) * (1 - transfer_coeff)
            return x

        insulate_functionality = make_functionality(
            name="insulate_heat",
            *insulate_heat_inputs,
            functionality_func=fn_insulate_heat
        )

        if plumbingIN is not None:
            if type == "heatOUT":
                coolant = make_coolant(
                    "coolant",
                    type,
                    insulate_functionality,
                    contain_functionality,
                    valve,
                    plumbingIN,
                    affect,
                )
            elif type == "standard" or type == "heatIN":
                coolant = make_coolant(
                    "coolant",
                    type,
                    insulate_functionality,
                    contain_functionality,
                    valve,
                    plumbingIN
                )
            elif type == "pump": 
                coolant = make_coolant(
                    "coolant",
                    type,
                    insulate_functionality,
                    contain_functionality,
                    valve,
                    plumbingIN,
                    affect,
                )
            else: 
                raise ValueError("Invalid type")
        else:
            if type == "heatOUT":
                coolant = make_coolant(
                    name="coolant",
                    type=type,
                    container_insulate=insulate_functionality,
                    container_store=contain_functionality,
                    valveOUT=valve,
                    plumbingIN=None,
                    affect=affect,
                )
            elif type == "standard" or type == "heatIN":
                coolant = make_coolant(
                    "coolant",
                    type,
                    insulate_functionality,
                    contain_functionality,
                    valve,
                )
            elif type == "pump":
                coolant = make_coolant(
                    name="coolant",
                    type=type,
                    container_insulate=insulate_functionality,
                    container_store=contain_functionality,
                    valveOUT=valve,
                    plumbingIN=None,
                    affect=affect,
                )
            else:
                raise ValueError("Invalid type")

    return plumbing_assembly
