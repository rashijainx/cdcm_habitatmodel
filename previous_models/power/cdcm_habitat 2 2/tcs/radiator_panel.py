"""Model of a radiator panel in TCS

Author:
    Rashi Jain

Date:
    1/23/2024 |
    2/29/2024 | Pep-8
"""

from cdcm import *
from cdcm_constructs import *

import datetime

__all__ = ["make_radiator_panel"]


def make_radiator_panel(
    name: str,
    clock: System,
    panel_age_rate: float,
    panel_interact_variable: float,
    panel_temperature_threshold: float,
    solar_irradiance: Variable,
    solar_threshold: float,
    coolant: System,
    controller: System,
    controller_threshold: float,
    **kwargs
) -> System:

    with System(name=name) as radiator_panel:

        def solar_irradiance_transform(solar_irr):
            return solar_irr / 1400.0

        age_rate = Variable(
            name="age_rate",
            value=panel_age_rate,
        )

        interact_variable = Variable(
            name="interact_variable",
            value=panel_interact_variable,
        )

        solar_irradiance_scaled = apply(
            solar_irradiance,
            solar_irradiance_transform,
            name="solar_irradiance_scaled"
        )

        # HARDWARE
        hardware = make_component(
            name="hardware",
            dt=clock.dt,
            aging_rate=age_rate,
            Ed=1.,
        )

        hardware_functionality_inputs = {
            hardware,
            interact_variable,
        }

        def fn_hardware_functionality(hardware, interact_variable) -> float:
            x = hardware*(1 - interact_variable)
            return x

        hardware_functionality = make_functionality(
            name="hardware_functionality",
            functionality_func=fn_hardware_functionality
        )

        radiator_panel_functionality_inputs = (
            solar_irradiance_scaled,
            solar_threshold,
            hardware_functionality,
            coolant.contamination,
            coolant.pressure,
            coolant.temperature,
            panel_temperature_threshold,
            coolant.volume,
            controller.rotate_component,
            controller_threshold
        )

        def fn_radiator_panel_functionality(
                solar_irradiance_scaled,
                solar_threshold,
                hardware_functionality,
                contamination,
                pressure,
                temperature,
                temperature_threshold,
                volume,
                rotator,
                rotator_threshold
        ) -> float:
            if solar_irradiance_scaled > solar_threshold:
                if rotator >= rotator_threshold:
                    if temperature > temperature_threshold:
                        x = hardware_functionality * (1 - contamination) *\
                            max(volume, pressure)
                    else:
                        x = hardware_functionality * (1 - contamination) *\
                            (temperature + 1 - temperature_threshold) *\
                            max(volume, pressure)
                else:
                    if temperature > temperature_threshold:
                        x = hardware_functionality * (1 - contamination) *\
                            max(volume, pressure) * \
                            (1 + solar_threshold - solar_irradiance_scaled)
                    else:
                        x = hardware_functionality * (1 - contamination) *\
                            (temperature + 1 - temperature_threshold) *\
                            max(volume, pressure) *\
                            (1 + solar_threshold - solar_irradiance_scaled)
            else:
                if temperature > temperature_threshold:
                    x = hardware_functionality * (1 - contamination) *\
                        max(volume, pressure)
                else:
                    x = hardware_functionality * (1 - contamination) *\
                        (temperature + 1 - temperature_threshold) *\
                        max(volume, pressure)
            return x

        radiator_panel_functionality = make_functionality(
            *radiator_panel_functionality_inputs,
            name="transfer_heat",
            functionality_func=fn_radiator_panel_functionality
        )

    return radiator_panel
