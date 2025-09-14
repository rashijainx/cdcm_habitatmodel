""" Model of the valve

Author:
    Rashi Jain

Date:
    2/3/2024
    2/28/2024 | Pep-8

"""

from cdcm import *
from cdcm_constructs import *

__all__ = ["make_valve"]


def make_valve(
    name: str,
    clock: System,
    valve_age_rate: float,
    valve_hardware_threshold: float,
    valve_interact_variable: float,
    valve_mechanism_failure: float,
    valve_control: float,
) -> System:

    with System(name=name) as valve:

        age_rate = Variable(
            name="age_rate",
            value=valve_age_rate
        )
        hardware_threshold = Variable(
            name="hardware_threshold",
            value=valve_hardware_threshold
        )
        interact_variable = Variable(
            name="interact_variable",
            value=valve_interact_variable
        )
        mechanism_failure = Variable(
            name="mechanism_failure",
            value=valve_mechanism_failure
        )
        control = Variable(
            name="control",
            value=valve_control
        )

        hardware = make_component(
            name="hardware",
            dt=clock.dt,
            aging_rate=age_rate,
            Ed=1.0,
        )

        def fn_hardware_functionality(
                hardware,
                interact_variable,
                mechanism_failure
        ) -> float:
            x = hardware*(1 - interact_variable)*(1 - mechanism_failure)
            return x

        hardware_functionality_inputs = (
            hardware,
            interact_variable,
            mechanism_failure,
        )

        hardware_functionality = make_functionality(
            name="hardware_functionality",
            *hardware_functionality_inputs,
            functionality_func=fn_hardware_functionality
        )

        valve_functionality_inputs = (
            hardware_functionality,
            hardware_threshold,
        )

        def fn_functionality(hardware_functionality, threshold):
            if hardware_functionality <= threshold:
                x = 0
            else:
                x = 1
            return x

        valve_functionality = make_functionality(
            name="regulate_flow",
            *valve_functionality_inputs,
            functionality_func=fn_functionality
        )

        position = Variable(
            name="position",
            value=0
        )

        @make_function(position)
        def calc_valve_state(
            hardware=hardware_functionality,
            threshold=hardware_threshold,
            value=control
        ):
            if hardware <= threshold:
                position = 1
            else:
                position = value
            return position

    return valve
