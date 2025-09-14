""" Model of Heaters in ETCS

Author:
    Noah Colasanti
    Rashi Jain

Date: 
    10/5/2023
    10/9/2023 - Integrated with Murali's model. 

"""

__all__ = ["make_heater"]

from cdcm import *
from cdcm_csc import *

def make_heater(
    clock: System,
    age_rate: NumOrVar,
    eccentric_amplitude: NumOrVar, 
    external_dust_rate: NumOrVar,
    external_meteorite_impact: NumOrVar, 
    **kwargs) -> System:

    with System(name = 'heater') as heater:
        
        # External Inputs
        power = make_component(name = 'power', nominal_health=1)

        temperature_sensor = make_component(name= 'temperature_sensor', nominal_health=1.0, Ed = 10.0)

        # SOFTWARE (also affected by Power and Sensor)
        human_updates_algorithm = make_component(
            name="human_updates_algorithm", nominal_health=1.0
        )

        eccentric_behavior_algorithm = make_component(
            name="eccentric_behavior_algorithm",
            dt=clock.dt,
            health_damage_rate=eccentric_amplitude
        )

        # HARDWARE (age) - also affected by power
        # Replace when functionality if below a threshold
        hardware = make_component(
            name="hardware",
            dt=clock.dt,
            aging_rate=age_rate,
            Ed=10.0,
        )
        
        dust = make_component(
            name= 'dust',
            dt=clock.dt,
            health_damage_rate= external_dust_rate,
        )

        # # We have a model for meteorite impact
        # metorite_impact = make_component(
        #     name = 'metorite_impact',
        #     clock=clock,
        #     health_damage_rate=external_meteorite_impact,
        # )

        agent_mishandling = make_component(name='agent_mishandling', nominal_health=1.0)

        # We want delamination value to change with solar irradiance model. 
        # Will make the change later. First, let's get the model to work. 

        delamination = make_component(
            name = 'delamination',
            nominal_health=1.0
        )
        
        heater_functionality_inputs = (
            power, 
            temperature_sensor,
            human_updates_algorithm,
            eccentric_behavior_algorithm,
            hardware,
            dust,
            agent_mishandling,
            delamination,
        )

        heater_functionality = make_functionality(*heater_functionality_inputs)

    return heater

