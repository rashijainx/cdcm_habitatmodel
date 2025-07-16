"""Model of a plumbing in TCS

Author:
    Rashi Jain

Date:
    1/26/2024 |
    2/21/2024 | Pep-8
    3/16/2024 | Simplified modeling

"""
from cdcm import *
from cdcm_constructs import *

from typing import Optional

__all__ = ["make_plumbing"]


def make_plumbing(
    name: str,
    clock: System,
    plumbing_age_rate: float,
    plumbing_interact_variable: float,
    plumbing_threshold: float,
    plumbing_heat_transfer: float,
) -> System:

    with System(name=name) as plumbing:

        age_rate = Variable(
            name="age_rate", 
            value=plumbing_age_rate
        )
        
        interact_variable = Variable(
            name="interact_variable",
            value=plumbing_interact_variable
        )
        threshold = Variable(
            name="threshold",
            value=plumbing_threshold
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
            name="contain_flow",
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
                transfer_coeff,
            ) -> float:
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

    return plumbing
