"""Model of an ETCS loop

Author:
    Rashi Jain

Date:
    4/16/2024 | Making one ETCS loop
"""
from cdcm import *
from cdcm_constructs import *

from .connector_assembly import make_converger_assembly
from .plumbing_assembly import make_plumbing_assembly
from .pump import make_pump
from .radiator_panel_unit import make_radiator_panel_unit

__all__ = ["make_etcs_loop"]


def make_etcs_loop(
    name: str,
    clock: System,
    heat_exchanger_quantity: int,
    rad_panel_unit_quantity: int,
    rad_panel_assembly_quantity: int,
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
    valve_hardware_threshold: float,
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
    pump_age_rate: float,
    pump_interact_variable: float,
    pump_mechanism_failure: float,
    pump_software_control: float,
    pump_power: float,
    pump_power_threshold: float,
    pump_contamination_threshold: float,
    heat_exchanger: list, 
) -> System:

    with System(name=name) as etcs_loop:

        plumbingOUT_hex_instances = []

        for i in range(heat_exchanger_quantity):
            
            plumbingOUT_hex = make_plumbing_assembly(
                f"plumbingOUT_hex{i+1}",
                "standard",
                clock,
                plumbing_age_rate,
                plumbing_interact_variable,
                plumbing_threshold_storage,
                plumbing_heat_transfer,
                valve_age_rate,
                valve_hardware_threshold,
                valve_interact_variable,
                valve_mechanism_failure,
                valve_control,
                heat_exchanger[i].plumbingEX_,
            )

            plumbingOUT_hex_instances.append(plumbingOUT_hex)

        convergerIN_rad = make_converger_assembly(
            "convergerIN_rad",
            clock,
            len(plumbingOUT_hex_instances),
            connector_age_rate,
            connector_interact_variable,
            connector_threshold,
            valve_age_rate,
            valve_hardware_threshold,
            valve_interact_variable,
            valve_mechanism_failure,
            valve_control,
            plumbingOUT_hex_instances
        )
 
        plumbingIN_rad_units = make_plumbing_assembly(
            "plumbingIN_rad_units",
            "standard",
            clock,
            plumbing_age_rate,
            plumbing_interact_variable,
            plumbing_threshold_storage,
            plumbing_heat_transfer,
            valve_age_rate,
            valve_hardware_threshold,
            valve_interact_variable,
            valve_mechanism_failure,
            valve_control,
            convergerIN_rad
        )

        plumbingOUT_rad_unit_instances = []
        for j in range(rad_panel_unit_quantity): 
                
            plumbingIN_rad_unit = make_plumbing_assembly(
                f"plumbingIN_rad_unit{j+1}",
                "standard",
                clock,
                plumbing_age_rate,
                plumbing_interact_variable,
                plumbing_threshold_storage,
                plumbing_heat_transfer,
                valve_age_rate,
                valve_hardware_threshold,
                valve_interact_variable,
                valve_mechanism_failure,
                valve_control,
                plumbingIN_rad_units
            )

            radiator_panel_unit = make_radiator_panel_unit(
                f"unit{j+1}",
                clock,
                rad_panel_assembly_quantity,
                solar_irradiance,
                solar_threshold,
                battery_age_rate,
                sensor_age_rate,
                sensor_power_threshold,
                sensor_drift_behavior,
                sensor_random_behavior,
                controller_age_rate,
                processor_age_rate,
                controller_interact_variable,
                controller_mechanism_failure,
                controller_power,
                controller_control,
                controller_control_efficiency,
                controller_sensor_threshold,
                plumbing_age_rate,
                plumbing_interact_variable,
                plumbing_threshold_storage,
                plumbing_heat_transfer,
                plumbing_rad_heat_transfer,
                valve_age_rate,
                valve_hardware_threshold,
                valve_interact_variable,
                valve_mechanism_failure,
                valve_control,
                panel_age_rate,
                panel_interact_variable,
                panel_temperature_threshold,
                controller_threshold,
                connector_age_rate,
                connector_interact_variable,
                connector_threshold,
                plumbingIN_rad_unit
            )

            plumbingOUT_rad_unit = make_plumbing_assembly(
                f"plumbingOUT_rad_unit{j+1}",
                "standard",
                clock,
                plumbing_age_rate,
                plumbing_interact_variable,
                plumbing_threshold_storage,
                plumbing_heat_transfer,
                valve_age_rate,
                valve_hardware_threshold,
                valve_interact_variable,
                valve_mechanism_failure,
                valve_control,
                radiator_panel_unit.converger
            )

            plumbingOUT_rad_unit_instances.append(plumbingOUT_rad_unit)

        convergerOUT_rad = make_converger_assembly(
            "convergerOUT_rad",
            clock,
            rad_panel_unit_quantity,
            connector_age_rate,
            connector_interact_variable,
            connector_threshold,
            valve_age_rate,
            valve_hardware_threshold,
            valve_interact_variable,
            valve_mechanism_failure,
            valve_control,
            plumbingOUT_rad_unit_instances
        )

        plumbingOUT_rad = make_plumbing_assembly(
            "plumbingOUT_rad",
            "standard",
            clock,
            plumbing_age_rate,
            plumbing_interact_variable,
            plumbing_threshold_storage,
            plumbing_heat_transfer,
            valve_age_rate,
            valve_hardware_threshold,
            valve_interact_variable,
            valve_mechanism_failure,
            valve_control,
            convergerOUT_rad
        )

        pump = make_pump(
            "pump",
            clock,
            pump_age_rate,
            pump_interact_variable,
            pump_mechanism_failure,
            pump_software_control,
            pump_power,
            pump_power_threshold,
            pump_contamination_threshold,
            plumbing_age_rate,
            plumbing_interact_variable,
            plumbing_threshold_storage,
            plumbing_heat_transfer,
            valve_age_rate,
            valve_hardware_threshold,
            valve_interact_variable,
            valve_mechanism_failure,
            valve_control,
            plumbingOUT_rad
        )

        plumbingOUT_pump = make_plumbing_assembly(
            "plumbingOUT_pump",
            "standard",
            clock, 
            plumbing_age_rate,
            plumbing_interact_variable,
            plumbing_threshold_storage,
            plumbing_heat_transfer,
            valve_age_rate,
            valve_hardware_threshold,
            valve_interact_variable,
            valve_mechanism_failure,
            valve_control,
            pump.plumbing
        )

        plumbingIN_hex_instances = []

        for i in range(heat_exchanger_quantity):
            
            plumbingIN_hex = make_plumbing_assembly(
                f"plumbingIN_hex{i+1}",
                "standard",
                clock,
                plumbing_age_rate,
                plumbing_interact_variable,
                plumbing_threshold_storage,
                plumbing_heat_transfer,
                valve_age_rate,
                valve_hardware_threshold,
                valve_interact_variable,
                valve_mechanism_failure,
                valve_control,
                plumbingOUT_pump,
            )

            plumbingIN_hex_instances.append(plumbingIN_hex)

    return etcs_loop
