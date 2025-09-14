"""Model of a connector in TCS

Author:
    Rashi Jain

Date:
    2/29/2024 |
    2/29/2024 | Pep-8
"""
from cdcm import *
from cdcm_constructs import *

from .valve import make_valve
from .coolant import make_pooled_coolant

__all__ = ["make_converger_assembly"]
 
def make_converger_assembly(
    name: str,
    clock: System,
    quantity: int,
    connector_age_rate: float,
    connector_interact_variable: float,
    connector_threshold: float,
    valve_age_rate: float,
    valve_threshold: float,
    valve_interact_variable: float,
    valve_mechanism_failure: float,
    valve_control: float,
    plumbing_systems: list,
    **kwargs
) -> System:

    with System(name=name) as connector:

        age_rate = Variable(
            name="age_rate",
            value=connector_age_rate,
        )
        interact_variable = Variable(
            name="interact_variable",
            value=connector_interact_variable,
        )
        threshold = Variable(
            name="threshold",
            value=connector_threshold,
        )
        interact_threshold = Variable(
            name="interact_threshold",
            value=1 - threshold.value
        )
        hardware = make_component(
            name="hardware",
            aging_rate=age_rate,
            dt=clock.dt,
            Ed=1.0,
        )

        def fn_contain_fluid(
            hardware,
            interact_variable,
            threshold,
            interact_threshold
        ) -> float:
            if hardware < threshold:
                if interact_variable > interact_threshold:
                    x = (hardware + (1 - threshold)) *\
                        (1 - interact_variable + interact_threshold)
                else:
                    x = (hardware + (1 - threshold))
            else:
                if interact_variable > interact_threshold:
                    x = (1 - interact_variable + interact_threshold)
                else:
                    x = 1.0
            return x

        contain_functionality_inputs = (
            hardware,
            interact_variable,
            threshold,
            interact_threshold,
        )

        contain_functionality = make_functionality(
            name="contain_fluid",
            *contain_functionality_inputs,
            functionality_func=fn_contain_fluid
        )

        insulate_heat_inputs = (
            interact_variable,
        )

        def fn_insulate_heat(
                interact_variable
            ) -> float:
            return interact_variable

        insulate_functionality = make_functionality(
            name="insulate_heat",
            *insulate_heat_inputs,
            functionality_func=fn_insulate_heat
        )

        if quantity == 2: 
            coolant = make_pooled_coolant(
                "coolant",
                plumbing_systems[0],
                plumbing_systems[1],
            )
        elif quantity == 3:
            coolant = make_pooled_coolant(
                "coolant",
                plumbing_systems[0],
                plumbing_systems[1],
                plumbing_systems[2],
            )
        elif quantity == 4:
            coolant = make_pooled_coolant(
                "coolant",
                plumbing_systems[0],
                plumbing_systems[1],
                plumbing_systems[2],
                plumbing_systems[3],
            )
        elif quantity == 5:
            coolant = make_pooled_coolant(
                "coolant",
                plumbing_systems[0],
                plumbing_systems[1],
                plumbing_systems[2],
                plumbing_systems[3],
                plumbing_systems[4],
            )
        elif quantity == 6:
            coolant = make_pooled_coolant(
                "coolant",
                plumbing_systems[0],
                plumbing_systems[1],
                plumbing_systems[2],
                plumbing_systems[3],
                plumbing_systems[4],
                plumbing_systems[5],
            )
        else: 
            raise ValueError("Quantity must be between 2 and 6")

        valve = make_valve(
            "valve",
            clock, 
            valve_age_rate,
            valve_threshold,
            valve_interact_variable,
            valve_mechanism_failure,
            valve_control,
        )
    return connector
