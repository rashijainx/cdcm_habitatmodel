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
    processor_age: float,
    controller_interact_variable: float,
    controller_mechanism_failure: float,
    controller_power: int,
    controller_control: int,
    controller_control_efficiency: float,
    sensor: System,
    controller_sensor_threshold: float,
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
        control = Variable(
            name="control",
            value=controller_control,
        )
        control_efficiency = Variable(
            name="control_efficiency",
            value=controller_control_efficiency,
        )
        sensor_threshold = Variable(
            name="sensor_threshold",
            value=controller_sensor_threshold
        )

        hardware = make_component(
            name="hardware",
            aging_rate=age_rate,
            dt=clock.dt,
            Ed=1.0,
        )

        hardware_functionality_inputs = (
            hardware.functionality,
            power,
            interact_variable,
            mechanism_failure,
        )

        def fn_hardware_functionality(
            hardware,
            power,
            interact_variable,
            mechansim_failure
        ) -> float:
            x = hardware * power *\
                (1.0 - interact_variable) * (1.0 - mechansim_failure)
            return x

        hardware_functionality = make_functionality(
            *hardware_functionality_inputs,
            name="hardware_functionality",
            functionality_func=fn_hardware_functionality
        )

        processor_age_rate = Variable(
            name="processor_age_rate",
            value=processor_age
        )
        processor = make_component(
            name="processor",
            dt=clock.dt,
            aging_rate=processor_age_rate,
            Ed=0.0,
        )

        def fn_controller_functionality(
            optical_sensor,
            sensor_threshold,
            control, processor,
            control_efficiency,
            hardware_functionality
        ) -> float:
            if (optical_sensor >= sensor_threshold or processor >= sensor_threshold) and control == 0:
                x = hardware_functionality * min(optical_sensor, processor)
            elif (optical_sensor >= sensor_threshold or processor >= sensor_threshold) and control == 1:
                x = hardware_functionality * control_efficiency
            elif (optical_sensor < sensor_threshold or processor < sensor_threshold) and control == 1:
                x = hardware_functionality * control_efficiency
            else:
                x = hardware_functionality * min(optical_sensor, processor)
            return x

        controller_functionality_inputs = (
            sensor.sense_source,
            sensor_threshold,
            control,
            processor,
            control_efficiency,
            hardware_functionality,
        )

        controller_functionality = make_functionality(
            *controller_functionality_inputs,
            name="rotate_component",
            functionality_func=fn_controller_functionality
        )

    return controller
