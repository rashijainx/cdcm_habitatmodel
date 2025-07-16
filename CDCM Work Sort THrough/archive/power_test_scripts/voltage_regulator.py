from cdcm import *
from cdcm_abstractions import *

from common_constructs import *
from wiring import *

__all__ = [
    "make_ssu", 
    "make_ddcu"
    ]

def make_ssu(
    name: str,
    clock: System,
    age_parameters: tuple,
    operating_temperatures: tuple,
    surviving_temperatures: tuple,
    temperature: Variable,
    voltage_rating: float,
    wiring_parameters: tuple, 
    power_generations: System,
) -> System:

    with System(name=name) as ssu:

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

        regulator_functionality_inputs = (
            aging.hardware,
            tolerance,
        )

        def make_regulator_functionality(
            hd=aging.hardware,
            tol=tolerance,
        ): 
            if hd > tol: 
                return hd
            else: 
                return 0.0
    
        regulator_functionality = make_functionality(
            *regulator_functionality_inputs,
            name="regulate_voltage",
            functionality_func=make_regulator_functionality
        )

        wiring = make_wiring(
            "wiring", 
            clock, 
            wiring_parameters
        )

        voltage_rating = Parameter(
            name="voltage_rating",
            value=voltage_rating,
        )

        voltage = Variable(
            name="voltage",
            value=voltage_rating
        )

        @make_function(voltage)
        def calc_ssu_voltage(
            v=voltage_rating,
            function=regulator_functionality,
            wire=wiring.transfer_electricity,
            power_gen=power_generations.generate_power,
        ):
            if wire == 1.0 and power_gen > 0.0: 
                return v * function 
            else: 
                return 0.0
   
    return ssu

def make_ddcu(
    name: str,
    clock: System,
    age_parameters: tuple,
    operating_temperatures: tuple,
    surviving_temperatures: tuple,
    temperature: Variable,
    voltage_rating: float,
    power_demand: float,
    wiring_parameters: tuple, 
    connecting_func: System,
) -> System:

    with System(name=name) as ddcu:

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

        regulator_functionality_inputs = (
            aging.hardware,
            tolerance,
        )

        def make_regulator_functionality(
            hd=aging.hardware,
            tol=tolerance,
        ): 
            if hd > tol: 
                return hd
            else: 
                return 0.0
    
        regulator_functionality = make_functionality(
            *regulator_functionality_inputs,
            name="regulate_voltage",
            functionality_func=make_regulator_functionality
        )

        wiring = make_wiring(
            "wiring", 
            clock, 
            wiring_parameters
        )

        voltage_rating = Parameter(
            name="voltage_rating",
            value=voltage_rating,
        )

        voltage = Variable(
            name="voltage",
            value=voltage_rating
        )

        @make_function(voltage)
        def calc_ddcu_voltage(
            v=voltage_rating,
            function=regulator_functionality,
            wire=wiring.transfer_electricity,
            power_gen=connecting_func.distribute_power,
        ):
            if wire == 1.0 and power_gen > 0.0: 
                return v * function 
            else: 
                return 0.0

        power_consumed = Variable(
            name="power_consumed",
            value=power_demand
        )

        power_demand = Variable(
            name="power_demand",
            value=power_demand
        )

        @make_function(power_consumed) 
        def calc_power_consumed(
            p=power_demand,
            function=regulator_functionality,
            wire=wiring.transfer_electricity,
            pin=connecting_func.downstream_load,
        ):
            if wire == 1.0 and function > 0.0 and pin > p: 
                return p
            else: 
                return 0.0

    return ddcu
