"""Making an ETCS model

Author:
    R Murali Krishnan
    
Date:
    10.04.2023
    
"""


__all__ = ["make_etcs_maintenance",
           "make_radiator_panel_assembly"]


from cdcm import *
from cdcm_csc_systems import *


def make_etcs_maintenance(clock, planet, lat, long, start_time, time_steps) -> System:
    """Model of the ETCS used to demonstrate a maintenance safety control""" 
    with System(name="etcs") as etcs:
        # Age 1%/ year
        actuator_age_rate = Parameter(
            name="actuator_age_rate", 
            value=1.0 / (24 * 365)
        )
        # Amplitude 0.25
        actuator_eccentric_amplitude = Parameter(
            name="actuator_erractic_amplitude", 
            value=0.0
        )
        # Age 1%/ year
        panels_age_rate = Parameter(
            name="panels_age_rate", 
            value=0.0, #1.0 / (24 * 365)
        )
        # Dust 1%/ year
        external_dust_rate = Parameter(
            name="external_dust_rate", 
            value=5.0 / (24 * 365)
        )
        # Meteorite Impact
        external_meteorite_impact = Parameter(
            name="external_meteorite_impact", 
            value=0.0, #0.5 / (24 * 365)
        )

        ext_env = SolarIrradiance("ext_env", clock, start_time, time_steps, planet=planet, lat=lat, long=long)

        controller = make_controller(
            clock,
            actuator_age_rate,
            actuator_eccentric_amplitude,
            external_dust_rate,
            external_meteorite_impact,
        )
        radiator_panel = make_radiator_panel(
            clock,
            panels_age_rate,
            external_dust_rate,
            controller,
            ext_env.solar_irradiance,
            external_meteorite_impact=external_meteorite_impact,
        )
    return etcs


def make_radiator_panel_assembly(
        clock: System, 
        solar_irradiance: Variable,
        actuator_age_rate: NumOrVar,
        actuator_eccentric_amplitude: NumOrVar,
        panels_age_rate: NumOrVar,
        external_dust_rate: NumOrVar
        ) -> System:
    """Make a radiator panel assembly"""

    with System(name="etcs") as etcs:
        # controller
        controller = make_controller(clock, 
                                     actuator_age_rate, 
                                     actuator_eccentric_amplitude, 
                                     external_dust_rate)

        # panels
        radiator_panels = make_radiator_panel(clock, 
                                              panels_age_rate, 
                                              external_dust_rate, 
                                              controller,
                                              solar_irradiance)
        functionality = make_functionality(controller, radiator_panels)
    
    return etcs