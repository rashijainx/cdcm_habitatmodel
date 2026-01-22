"""Radiator Panel Assemblies

Author:
    Rashi Jain

Date:
    02.16.2024
    02.29.2024 | Pep-8
    03.18.2024 | Model Update
"""

from cdcm import *
from cdcm_constructs import *
from typing import Optional

from .plumbing_assembly import make_plumbing_assembly

__all__ = ["make_radiator_panel_assembly"]


def make_radiator_panel_assembly(
    name: str,
    clock: System,
    solar_irradiance: Variable,
    solar_threshold: float, 
    plumbing_age_rate: float,
    plumbing_interact_variable: float,
    plumbing_threshold_storage: float,
    plumbing_heat_transfer: float,
    valve_age_rate: float,
    valve_threshold: float,
    valve_interact_variable: float,
    valve_mechanism_failure: float,
    valve_control: float,
    panel_age_rate: float,
    panel_interact_variable: float,
    panel_temperature_threshold: float,
    controller: System,
    controller_threshold: float,
    plumbing: Optional[System[None]] = None,
) -> System:

    with System(name=name) as radiator_panel_assembly:

        if plumbing is not None:
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
                valve_control,
                plumbing,
            )
        else:
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
                valve_control,
            )

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
            health_damage_rate=age_rate,
            Ed=1.0,
        )

        # hardware_functionality_inputs = {
        #     hardware,
        #     interact_variable,
        # }

        # def fn_hardware_functionality(hardware, interact_variable) -> float:
        #     x = hardware * (1 - interact_variable)
        #     return x

        # hardware_functionality = make_functionality(
        #     name="hardware_functionality",
        #     functionality_func=fn_hardware_functionality
        # )

        radiator_panel_functionality_inputs = (
            solar_irradiance_scaled,
            solar_threshold,
            hardware,
            plumbingIN.coolant.contamination,
            plumbingIN.coolant.pressure,
            plumbingIN.coolant.temperature,
            panel_temperature_threshold,
            plumbingIN.coolant.volume,
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

        plumbingOUT = make_plumbing_assembly(
            "plumbingOUT",
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
            plumbingIN,
            radiator_panel_functionality,
        )

    return radiator_panel_assembly
