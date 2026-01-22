"""
Modified model of a controller

Author: 
    Rashi Jain
    R Murali Krishnan

Date: 
    9/21/2023
    10/6/2023 - Modified to Integrate Murali's format. 

"""

__all__ = ["make_radiator_panel"]

from cdcm import *
from cdcm_csc import *

import datetime


def make_radiator_panel(
    clock: System, 
    age_rate: Parameter, 
    external_dust_rate: Parameter, 
    # external_meteorite_impact: Parameter, 
    solar_irradiance: Variable,
    controller: System,
    **kwargs    
    ) -> System:

    with System(name="radiator_panel") as radiator_panel:

        # External Inputs
        power = make_component(name="power", nominal_health=1)

        # Solar Irradiance
        def solar_irradiance_transform(solar_irr):
            return solar_irr / 1400.0

        solar_irradiance_scaled = apply(solar_irradiance, solar_irradiance_transform, name="solar_irradiance_scaled")

        # HARDWARE (age)
        hardware = make_component(
            name="panels_hardware",
            dt=clock.dt,
            aging_rate=age_rate,
            Ed=70.0,
        )
        # EXTERNAL HARDWARE (dust, meteorite impact)
        dust = make_component(
            name="dust",
            dt=clock.dt,
            health_damage_rate=external_dust_rate,
        )

        # panels_meteorite = make_component(
        #     name="panels_meteorite",
        #     clock=clock,
        #     health_damage_rate=external_meteorite_impact,
        #     health_state_func=linear_function(),
        # )

        agent_mishandling = make_component(name="agent_mishandling", nominal_health=1.0)

        # @murakrishn: Functionality model required from Rashi
        def fn_functionality(power,aging,dust,agent,solar,controller) -> float:
            """Functionality model of the radiator panels"""
            if controller >= 0.5:
                x = power*aging*dust*agent*(1 - solar)*controller
            else:  # controller < 0.5
                x = power*aging*dust*agent*(1 - solar)*0.5
            return x
        
        radiator_panel_functionality_inputs = (
            power,
            hardware,
            dust,
            agent_mishandling,
            solar_irradiance_scaled,
            controller,
        )

        radiator_panel_functionality = make_functionality(
            *radiator_panel_functionality_inputs,
            functionality_func=fn_functionality
        )

    return radiator_panel
