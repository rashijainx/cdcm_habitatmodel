"""Model of ammonia working fluid in ETCS

Author: 
    Darin Lin

Date: 
    10/6/2023

"""

from cdcm import *
from cdcm_csc import *


def make_ammonia(
    clock: System,
    contamination_rate: NumOrVar,
    radiator_panel: System,
    solar_irradiance: Variable
    ) -> System:

    with System(name="ammonia") as ammonia:

        contamination = make_component(
            name="contamination",
            dt=clock.dt,
            health_damage_rate=contamination_rate
        )   

        def solar_irradiance_transform(solar_irr):
            return solar_irr / 1400.0

        solar_irradiance_scaled = apply(solar_irradiance, solar_irradiance_transform, name="solar_irradiance_scaled")       

        temperature_rate = Variable(
            name="temperature_rate",
            value=0.0
        )

        temperature = make_component(
            name="temperature",
            dt=clock.dt,
            nominal_health=0.5,
            health_damage_rate=temperature_rate
        )

        @make_function(temperature_rate)
        def update_temperature_rate(temperature=temperature.functionality,
                                    solar_irradiance=solar_irradiance_scaled, 
                                    radiator_panel=radiator_panel.functionality):
            if solar_irradiance > radiator_panel:
                return (solar_irradiance - radiator_panel) * 0.01
            elif temperature < 0.5:
                return -0.01
            else:
                return 0

        ammonia_functionality_inputs = (
            contamination,
            temperature
        )

        def ammonia_functionality_function(contamination, temperature):
            if not (0.2 <= temperature <= 0.8):
                return 0
            else:
                return contamination

        ammonia_functionality = make_functionality(
            *ammonia_functionality_inputs,
            name="ammonia_functionality",
            functionality_func=ammonia_functionality_function
        )

    return ammonia