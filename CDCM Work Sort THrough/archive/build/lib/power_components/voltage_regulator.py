from cdcm import *
from cdcm_abstractions import *

from .wiring import *

__all__ = [
    "make_ssu", 
    "make_ddcu"
    ]

def make_ssu(
    name: str,
    clock: System,
    aging_rate: float,
    operating_temperature: tuple,
    surviving_temperature: tuple,
    temperature: Variable,
    voltage_rating: Variable,
    threshold: tuple,
    wiring_parameters: tuple, 
    power: System,
) -> System:

    with System(name=name) as ssu:

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

        regulator_functionality = make_functionality(
            hardware,
            name="regulate_voltage"
        )

        voltage = Variable (
            name="voltage", 
            value=voltage_rating, 
        )

        function_threshold = Variable(
            name="function_threshold", 
            value=threshold[0]
        )

        power_threshold = Variable(
            name="power_threshold", 
            value=threshold[1]
        )

        wiring = make_wiring(
            "wiring", 
            clock, 
            wiring_parameters
        )

        @make_function(voltage)
        def calc_ssu_voltage(
            thresh=function_threshold,
            v=voltage_rating,
            function=regulator_functionality,
            wire=wiring.transfer_electricity, 

        ):
            if function > thresh and wire == 1: 
                return v
            else: 
                return 0.0
            
        heat = Variable(
            name="heat",
            value=0.0
        )

        @make_function(heat)
        def calc_heat(
            power_in=power.generate_power,
            power_thresh_req=power_threshold,
        ):
            if power_in > power_thresh_req: 
                return (power_in - power_thresh_req)*0.1
            else: 
                return 0.0
   
    return ssu

def make_ddcu(
    name: str,
    clock: System,
    aging_rate_parameters: tuple,
    operating_temperature: tuple,
    surviving_temperature: tuple,
    temperature: Variable,
    voltage_rating: Variable,
    wiring_parameters: tuple, 
    connecting_func: System,
) -> System:

    with System(name=name) as ddcu:

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
            value=aging_rate_parameters[0]
        )

        aging_rate = Variable(
            name="aging_rate",
            value=aging_rate_parameters[0]
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

        wiring = make_wiring(
            "wiring", 
            clock, 
            wiring_parameters,
        )

        threshold = Variable(
            name="threshold", 
            value=aging_rate_parameters[1]
        )

        regulator_functionality_inputs = (
            hardware, 
            threshold
        ) 

        def make_regulator_functionality(
            hd=hardware,
            th=threshold,
        ): 
            if hd < th: 
                return 0 
            else: 
                return 1

        regulator_functionality = make_functionality(
            *regulator_functionality_inputs,
            name="regulate_voltage",
            functionality_func=make_regulator_functionality
        )

        voltage = Variable (
            name="voltage", 
            value=voltage_rating.value, 
        )

        @make_function(voltage)
        def calc_ddcu_voltage(
            v=voltage_rating,
            function=regulator_functionality,
            wire=wiring.transfer_electricity, 
            connection=connecting_func.functionality,
        ):
            if function == 1 and wire == 1 and connection == 1:
                return v
            else: 
                return 0.0
   
    return ddcu
