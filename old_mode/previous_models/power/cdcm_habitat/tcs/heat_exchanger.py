""" Modeel of a Heat Exchanger in TCS

Author:
    Rashi Jain

Date:
    3/25/2024 | Initial Model

"""

from cdcm import *
from cdcm_constructs import *

from .plumbing_assembly import make_plumbing_assembly

from typing import Optional

__all__ = ["make_heat_exchanger"]

def make_heat_exchanger(
    name: str,
    clock: System,
    age_rate: float,
    interact_variable: float,
    threshold: float,
    plumbing_age_rate: float,
    plumbing_interact_variable: float,
    plumbing_threshold_storage: float,
    plumbing_heat_transfer: float,
    valve_age_rate: float,
    valve_threshold: float,
    valve_interact_variable: float,
    valve_mechanism_failure: float,
    valve_control: float,
    plumbing_ex: Optional[System[None]] = None,
    plumbing_in: Optional[System[None]] = None,
) -> System:

    with System(name=name) as heat_exchanger:

        age_rate = Variable(
            name="age_rate",
            value=age_rate,
        )
        threshold = Variable(
            name="threshold",
            value=threshold,
        )
        interact_variable = Variable(
            name="interact_variable",
            value=interact_variable,
        )

        hardware = make_component(
            name="hardware",
            dt=clock.dt,
            aging_rate=age_rate,
            Ed=1.0,
        )

        hardware_functionality_inputs=(
            hardware,
            interact_variable,
            threshold,
        )

        def fn_hardware(
            hardware,
            interact_variable,
            threshold,
        ) -> float:
            if hardware < threshold: 
                x = hardware * (1 - interact_variable)
            else: 
                x = 1 - interact_variable
            return x

        hardware_functionality = make_functionality(
            name="hardware_functionality",
            *hardware_functionality_inputs,
            functionality_func = fn_hardware
        )

        plumbingEX = make_plumbing_assembly(
            "plumbingEX",
            "heatIN",
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
            plumbing_ex,
        )

        plumbingIN = make_plumbing_assembly(
            "plumbingIN",
            "heatIN",
            clock,
            plumbing_age_rate,
            plumbing_interact_variable,
            plumbing_threshold_storage,
            plumbing_heat_transfer,
            valve_age_rate,
            valve_threshold,
            valve_interact_variable,
            valve_mechanism_failure,
            0.0,
            plumbing_in,
        )

        plumbingEX_ = make_plumbing_assembly(
            "plumbingEX_",
            "heatOUT",
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
            plumbingEX,
            plumbingIN.coolant.temperature,
        )

        plumbingIN_ = make_plumbing_assembly(
            "plumbingIN_",
            "heatOUT",
            clock,
            plumbing_age_rate,
            plumbing_interact_variable,
            plumbing_threshold_storage,
            plumbing_heat_transfer,
            valve_age_rate,
            valve_threshold,
            valve_interact_variable,
            valve_mechanism_failure,
            0.0,
            plumbingIN,
            plumbingEX.coolant.temperature
        )

        functionality_inputs = (
            hardware_functionality,
            plumbingEX_.coolant.temperature,
            plumbingIN_.coolant.temperature,
        )

        heat_exchanger_functionality = make_functionality(
            *functionality_inputs,
        )

    return heat_exchanger