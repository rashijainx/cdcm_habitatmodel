"""
Modified model of a controller

Author: 
    Rashi Jain
    R Murali Krishnan

Date: 
    9/21/2023
    9/21/2023

"""


__all__ = ["make_radiator_panel"]


from cdcm import *
from cdcm_csc import *



def make_radiator_panel(
    clock: System, 
    panels_age_rate: Parameter, 
    external_dust_rate: Parameter, 
    controller: System,
    solar_irradiance: Variable,
    *,
    external_meteorite_impact: Parameter=None, 
    **kwargs    
    ) -> System:
    """Constructor procedure for ETCS radiator panels
    
    Arguments:
    ----------
    clock                       :   System
        Clock system for the simulation
    panels_age_rate             :   Parameter
        Parameter that specifies the aging rate of the panels
    external_dust_rate          :   Parameter
        Parameter that specifies the external dust rate
    external_meteorite_impact   :   Parameter
        Parameter that specifies the external meteorite impact rate
    controller                  : System
        Controller system of the radiator panels

    Returns:
        Radiator Panels :: System
            System model of the radiator panels
    """
    with System(name="radiator_panel") as radiator_panel:

        # External Inputs
        power = make_component(name="power", nominal_health=1)

        # Scaled solar irradiance
        def solar_irradiance_transform(solar_irr):
            return 1.0 - solar_irr / 1400.0

        solar_irradiance_scaled = apply(solar_irradiance, solar_irradiance_transform, name="solar_irradiance_scaled")

        # Hardware of the panel
        # | has an aging behavior
        # | Can be affected by a meteorite impact event
        # import pdb; pdb.set_trace()
        hardware = make_component(name="hardware",
                                  dt=clock.dt, 
                                  aging_rate=panels_age_rate,
                                  Ed=70.0)
        # EXTERNAL HARDWARE (dust, meteorite impact)
        dust = make_component(name="dust",
                              dt=clock.dt,
                              health_damage_rate=external_dust_rate)

        # A component of the radiator that can be affected by `meteorite`
        # panels_meteorite = make_component(
        #     name="meteorite",
        #     clock=clock,
        #     health_damage_rate=external_meteorite_impact,
        # )

        agent_mishandling = make_component(name="agent_mishandling", nominal_health=1.0)

        def fn_functionality(power,aging,dust,meteorite,agent,solar,controller) -> float:
            """Functionality model of the radiator panels"""
            if controller >= 0.5:
                x = power*aging*dust*meteorite*agent*solar*controller
            else:  # controller < 0.5
                x = power*aging*dust*meteorite*agent*solar*0.5
            return x

        
        radiator_panel_functionality = make_functionality(
            power,
            hardware.age,
            dust,
            hardware.health,
            agent_mishandling,
            solar_irradiance_scaled,
            controller,
            functionality_func=fn_functionality
        )
    return radiator_panel



