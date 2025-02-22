from cdcm import *
from cdcm_abstractions import *

from common_constructs import *
from voltage_regulator import *

__all__ = ["make_solar_array",
           "make_integrated_array"]
    
def make_solar_array(
    name: str,
    clock: System,
    solar_irradiance: Variable,
    age_parameters: tuple,
    operating_temperatures: tuple,
    surviving_temperatures: tuple,
    temperature: Variable,
    power_multiplier: float,
    operational_status: float,

) -> System:

    with System(name=name) as solar_array:

        aging = make_aging_component(
            "aging",
            clock,
            age_parameters,
            operating_temperatures,
            surviving_temperatures,
            temperature,
        )

        tolerance = Variable(
            name="tolerance",
            value=age_parameters[2]
        )

        multiplier = Parameter(
            name="multiplier",
            value=power_multiplier
        )

        solar_array_generative_capacity_inputs = (
            aging.hardware, 
            tolerance,
            multiplier,
            solar_irradiance
        )

        def make_solar_array_generative_capacity(
                hd=aging.hardware,
                tol=tolerance,
                m=multiplier,
                irr=solar_irradiance,
        ): 
            if hd > tol and irr > 0:
                return m*irr
            elif hd < tol and hd > (1 - tol) and irr > 0: 
                return m*irr*hd
            else:
                return 0.0

        solar_array_generative_capacity_functionality = make_functionality(
            *solar_array_generative_capacity_inputs,
            name="generative_capacity",
            functionality_func=make_solar_array_generative_capacity
        )

        os = Parameter(
            name="operational_status",
            value=operational_status
        )

        solar_array_power_inputs = (
            solar_array_generative_capacity_functionality,
            os,
        )
    
        def make_solar_array_power_generation(
            
            capacity=solar_array_generative_capacity_functionality.value,
            o=os,
            
        ): 
            if o == 1: 
                return capacity
            else: 
                return 0.0

        solar_array_power_generation = make_functionality(
            *solar_array_power_inputs,
            name="generate_power",
            functionality_func=make_solar_array_power_generation
        )

    return solar_array

def make_integrated_array(
    name: str,
    clock: System,
    solar_irradiance: Variable,
    temperature: Variable,
    solar_array_parameters: tuple,
    solar_operating_temperature: tuple,
    solar_surviving_temperature: tuple,
    solar_array_power_multiplier: float,
    solar_array_operational_status: float,
    ssu_age_parameters: tuple,
    ssu_operating_temperature: tuple,
    ssu_surviving_temperature: tuple,
    ssu_voltage_rating: float,
    wiring_parameters: tuple,
) -> System:
    with System(name=name) as integrated_array:

        solar_array = make_solar_array(
            "array",
            clock,
            solar_irradiance,
            solar_array_parameters,
            solar_operating_temperature,
            solar_surviving_temperature,
            temperature,
            solar_array_power_multiplier,
            solar_array_operational_status,
        )

        ssu = make_ssu(
            "ssu",
            clock,
            ssu_age_parameters,
            ssu_operating_temperature,
            ssu_surviving_temperature,
            temperature,
            ssu_voltage_rating,
            wiring_parameters,
            solar_array,
        )

    return integrated_array