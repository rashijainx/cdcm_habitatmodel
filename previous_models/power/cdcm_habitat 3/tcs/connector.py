"""Model of a connector in TCS

Author:
    Rashi Jain

Date:
    2/29/2024 |
    2/29/2024 | Pep-8
"""
from cdcm import *
from cdcm_constructs import *

__all__ = ["make_connector"]


def make_connector(
    name: str,
    clock: System,
    connector_age_rate: float,
    connector_interact_variable: float,
    connector_threshold: float,
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

        def fn_connector_functionality(
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

        connector_functionality_inputs = (
            hardware,
            interact_variable,
            threshold,
            interact_threshold,
        )

        connector_functionality = make_functionality(
            *connector_functionality_inputs,
            functionality_func=fn_connector_functionality
        )

    return connector
