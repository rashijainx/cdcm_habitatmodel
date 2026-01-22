"""
ETCS Models 

Author:
    Rashi Jain

Date: 10/17/2023 

""" 

__all__ = ["make_panel_assembly"] 

from cdcm import * 
from cdcm_csc_systems import * 

def make_panel_assembly( 
        instance_name: str,
        clock: System, 
        solar_irradiance: Variable, 
        external_dust_rate: NumOrVar, 
        actuator_age_rate: NumOrVar,
        actuator_eccentric_amlitude: NumOrVar,
        panels_age_rate: NumOrVar,  
) -> System: 
    
    with System(name=instance_name) as panel_assembly: 
        # Controller  
        controller=make_controller(clock,
                                actuator_age_rate,
                                actuator_eccentric_amlitude,
                                external_dust_rate, 
                                )

        # Radiator Panel 
        radiator_panels = make_radiator_panel(clock,
                                            panels_age_rate, 
                                            external_dust_rate,
                                            solar_irradiance,
                                            controller
                                            )
        
    return panel_assembly
