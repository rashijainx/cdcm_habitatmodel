from cdcm import *
from cdcm_abstractions import *

from .voltage_regulator import *

__all__ = ["make_solar_array",
           "make_integrated_array"]

def make_solar_array(
    name: str,
    clock: System,
    solar_irradiance: Variable,
    aging_rate: Variable,
    operating_temperature: tuple,
    surviving_temperature: tuple,
    temperature: Variable,
    number_of_panels: Variable,
    panel_capacity: Variable,
    operational_status: Variable,
    # Controller: Variable, # Will be changed to a System
) -> System:

    with System(name=name) as solar_array:

        operating_temp_min = Variable(
            name="operating_temp_min",
            value=operating_temperature[0]
        )
        operating_temp_max = Variable(
            name="operating_temp_max",
            value=operating_temperature[1]
        )
        surviving_temp_min = Variable(
            name="surviving_temp_min",
            value=surviving_temperature[0]
        )
        surviving_temp_max = Variable(
            name="surviving_temp_max",
            value=surviving_temperature[1]
        )

        age_rate = Variable(
            name="age_rate",
            value=aging_rate
        )

        @make_function(age_rate)
        def calc_age_rate(
            temp=temperature,
            omin=operating_temp_min,
            omax=operating_temp_max,
            smin=surviving_temp_min,
            smax=surviving_temp_max,
            ar=aging_rate
        ):
            if temp < omin or temp > omax:
                x = 1.0
            elif temp < smin or temp > smax:
                x = ar*2.0
            else:
                x = ar
            return x

        hardware = make_component(
            name="hardware",
            health_damage_rate=age_rate,
            dt=clock.dt,
            Ed=1.0
        )

        solar_array_inputs = (
            hardware, 
            number_of_panels,
            panel_capacity,
        )

        solar_array_functionality = make_functionality(
            *solar_array_inputs,
            name="generative_capacity",
        )

        solar_array_power_inputs = (
            solar_array_functionality, 
            solar_irradiance,
            operational_status,
        )
    
        def make_solar_array_power_generation(
            capacity=solar_array_functionality,
            irradiance=solar_irradiance,
            os=operational_status,
        ): 
            if irradiance > 0:
                if os == 1: 
                    return capacity*irradiance
                else: 
                    return 0.0
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
    aging_rate: tuple,
    operating_temperature: tuple,
    surviving_temperature: tuple,
    temperature: Variable,
    number_of_panels: Variable,
    panel_capacity: Variable,
    operational_status: Variable,
    voltage_rating: Variable,
    ssu_threshold: tuple,
    wiring: tuple,
) -> System:
    with System(name=name) as integrated_array:

        solar_array = make_solar_array(
            "array",
            clock,
            solar_irradiance,
            aging_rate[0],
            operating_temperature,
            surviving_temperature,
            temperature,
            number_of_panels,
            panel_capacity,
            operational_status,
        )

        ssu = make_ssu(
            "ssu",
            clock,
            aging_rate[1],
            operating_temperature,
            surviving_temperature,
            temperature,
            voltage_rating,
            ssu_threshold,
            wiring,
            solar_array,
        )

    return integrated_array