from cdcm import *
from cdcm_abstractions import *


__all__ = ["make_aging_component"]

def make_aging_component(
    name: str,
    clock: System,
    age_parameters: tuple,
    operating_temperatures: tuple,
    surviving_temperatures: tuple,
    temperature: Variable,
) -> System: 
        
    with System(name=name) as aging_component:
        operating_temp_min = Variable(
            name="operating_temp_min",
            value=operating_temperatures[0]
        )
        operating_temp_max = Variable(
            name="operating_temp_max",
            value=operating_temperatures[1]
        )
        surviving_temp_min = Variable(
            name="surviving_temp_min",
            value=surviving_temperatures[0]
        )
        surviving_temp_max = Variable(
            name="surviving_temp_max",
            value=surviving_temperatures[1]
        )

        age_parameter = Parameter(
            name="age_parameters",
            value=age_parameters[0]
        )

        radiation = Variable(
            name="radiation",
            value=age_parameters[1]
        ) 

        age_rate = Variable(
            name="age_rate",
            value=0.0
        )

        @make_function(age_rate)
        def calc_age_rate(
            temp=temperature,
            omin=operating_temp_min,
            omax=operating_temp_max,
            smin=surviving_temp_min,
            smax=surviving_temp_max,
            ar=age_parameter,
            radiation=radiation,
        ):
            if temp < omin or temp > omax:
                return 1.0
            elif temp < smin or temp > smax:
                return ar*(2.0 + (radiation - 1.0))
            else:
                return 0.0

        hardware = make_component(
            name="hardware",
            health_damage_rate=age_rate,
            dt=clock.dt,
            Ed=1.0
        )
    return aging_component