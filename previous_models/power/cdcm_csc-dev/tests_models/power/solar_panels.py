"""
Model of Solar Panel

Author: 
    Noah Colasanti
    Rashi Jain

Date: 
    10/6/2023

"""


from cdcm import *
from cdcm_csc import *
from controller import make_controller


def make_solar_panel(
    clock: System, 
    panels_age_rate: Parameter, 
    external_dust_rate: Parameter, 
    external_meteorite_impact: Parameter, 
    controller: System,
    **kwargs    
    ) -> System:

    with System(name="solar_panel") as solar_panel:

        # External Inputs
        panels_power = make_component(name="panels_power", nominal_health=1)

        # HARDWARE (age)
        panels_hardware = make_component(
            name="panels_hardware",
            dt=clock.dt,
            aging_rate=panels_age_rate,
            aging_func=linear_function(),
        )
        # EXTERNAL HARDWARE (dust, meteorite impact)
        panels_dust = make_component(
            name="panels_dust",
            dt=clock.dt,
            health_damage_rate=external_dust_rate,
            health_state_func=linear_function(),
        )

        # panels_meteorite = make_component(
        #     name="panels_meteorite",
        #     clock=clock,
        #     health_damage_rate=external_meteorite_impact,
        #     health_state_func=linear_function(),
        # )

        agent_mishandling = make_component(name="agent_mishandling", nominal_health=1.0)

        
        solar_panel_functionality = make_functionality(
            panels_power,
            panels_hardware,
            panels_dust,
            agent_mishandling,
            controller,
            name="solar_panel_functionality",
        )
    return solar_panel

