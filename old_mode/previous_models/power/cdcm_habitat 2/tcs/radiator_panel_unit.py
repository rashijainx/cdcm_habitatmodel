"""Radiator Panel Assemblies

Author:
    Rashi Jain

Date:
    03.20.2024
"""

from cdcm import *
from cdcm_constructs import *
from typing import Optional

from .controller import make_controller
from .sensor_assembly import make_sensor_assembly
from .plumbing_assembly import make_plumbing_assembly
from .radiator_panel_assembly import make_radiator_panel_assembly
from .connector_assembly import make_converger_assembly

__all__ = ["make_radiator_panel_unit"]


def make_radiator_panel_unit( 
    name: str,
    clock: System,
    quantity: int,
    solar_irradiance: Variable,
    solar_threshold: float,
    battery_age_rate: float,
    sensor_age_rate: float,
    sensor_power_threshold: float,
    sensor_drift_behavior: float,
    sensor_random_behavior: float,
    controller_age_rate: float,
    processor_age_rate: float,
    controller_interact_variable: float,
    controller_mechanism_failure: float,
    controller_power: int,
    controller_control: int,
    controller_control_efficiency: float,
    controller_sensor_threshold: float,
    plumbing_age_rate: float,
    plumbing_interact_variable: float,
    plumbing_threshold_storage: float,
    plumbing_heat_transfer: float,
    plumbing_rad_heat_transfer: float,
    valve_age_rate: float,
    valve_threshold: float,
    valve_interact_variable: float,
    valve_mechanism_failure: float,
    valve_control: float,
    panel_age_rate: float,
    panel_interact_variable: float,
    panel_temperature_threshold: float,
    controller_threshold: float,
    connector_age_rate: float,
    connector_interact_variable: float,
    connector_threshold: float,
    plumbing: Optional[System[None]] = None,
) -> System:

    with System(name=name) as radiator_panel_unit:

        sensor = make_sensor_assembly(
            "sensor",
            clock,
            battery_age_rate,
            sensor_age_rate,
            sensor_power_threshold,
            sensor_drift_behavior,
            sensor_random_behavior,
        )

        controller = make_controller(
            "controller",
            clock,
            controller_age_rate,
            processor_age_rate,
            controller_interact_variable,
            controller_mechanism_failure,
            controller_power,
            controller_control,
            controller_control_efficiency,
            sensor,
            controller_sensor_threshold,
        )

        plumbingOUT_instances = []
        for i in range(quantity):
            plumbingIN = make_plumbing_assembly(
                f"plumbingIN_panel{i+1}",
                "standard",
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
                plumbing
            )
            
            radiator_panel = make_radiator_panel_assembly(
                f"panel{i+1}",
                clock,
                solar_irradiance,
                solar_threshold,
                plumbing_age_rate,
                plumbing_interact_variable,
                plumbing_threshold_storage,
                plumbing_rad_heat_transfer,
                valve_age_rate,
                valve_threshold,
                valve_interact_variable,
                valve_mechanism_failure,
                valve_control,
                panel_age_rate,
                panel_interact_variable,
                panel_temperature_threshold,
                controller,
                controller_threshold,
                plumbingIN,
            )

            plumbingOUT = make_plumbing_assembly(
                f"plumbingOUT_panel{i+1}",
                "standard",
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
                radiator_panel.plumbingOUT,
            )

            plumbingOUT_instances.append(plumbingOUT)

        converger = make_converger_assembly(
            "converger",
            clock,
            quantity,
            connector_age_rate,
            connector_interact_variable,
            connector_threshold,
            valve_age_rate,
            valve_threshold,
            valve_interact_variable,
            valve_mechanism_failure,
            valve_control,
            plumbingOUT_instances,
        )

    return radiator_panel_unit
