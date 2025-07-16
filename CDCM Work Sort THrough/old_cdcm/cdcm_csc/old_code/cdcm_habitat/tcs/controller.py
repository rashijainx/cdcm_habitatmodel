"""Model of a controller in TCS

Author:
    Rashi Jain
    R Murali Krishnan

Date:
    1/22/2024 |
    2/26/2024 | Pep-8
"""
from cdcm import *
from cdcm_constructs import *

__all__ = ["make_controller"]


def make_controller(
    name: str,
    clock: System,
    controller_age_rate: float,
    controller_interact_variable: float,
    controller_mechanism_failure: float,
    controller_power: float,
    controller_power_threshold: float,
    **kwargs
) -> System:

    with System(name=name) as controller:

        age_rate = Variable(
            name="age_rate",
            value=controller_age_rate,
        )
        interact_variable = Variable(
            name="interact_variable",
            value=controller_interact_variable,
        )
        mechanism_failure = Variable(
            name="mechanism_failure",
            value=controller_mechanism_failure,
        )
        power = Variable(
            name="power",
            value=controller_power,
        )

        power_threshold = Variable(
            name="power_threshold",
            value=controller_power_threshold,
        )

        hardware = make_component(
            name="hardware",
            aging_rate=age_rate,
            dt=clock.dt,
            Ed=1.0,
        )

        controller_functionality_inputs = (
            hardware.functionality,
            power,
            power_threshold,
            interact_variable,
            mechanism_failure,
        )

        def fn_controller_functionality(
            hardware,
            power,
            power_threshold,
            interact_variable,
            mechanism_failure
        ) -> float:
            if power < power_threshold: 
                x = 0.0
            else: 
                x = hardware * power *\
                    (1.0 - interact_variable) * (1.0 - mechanism_failure)
            return x

        controller_functionality = make_functionality(
            *controller_functionality_inputs,
            name="rotate_component",
            functionality_func=fn_controller_functionality
        )

    return controller
