from cdcm import *
from cdcm_abstractions import *

import random

from command_and_control_components import *

__all__ = ["make_dcsu"]


def make_dcsu(
    name: str,
    clock: System,
    dcsu_age_parameters: tuple,
    min_power_req: Parameter,
    voltage_rating: Variable,
    sensor: System,
    power_generation: System,
    power_demands: Variable,
    number_of_batteries: Parameter,
) -> System:

    with System(name=name) as dcsu:

        age_rate = Variable(
            name="age_rate",
            value=dcsu_age_parameters[0]
        )

        tolerance = Variable(
            name="tolerance",
            value=dcsu_age_parameters[1]
        )

        hardware = make_component(
            name="hardware",
            health_damage_rate=age_rate,
            dt=clock.dt,
            Ed=1.0
        )
    
        dcsu_functionality_inputs = (
            hardware,
            tolerance,
            power_generation.ssu.regulate_voltage,
            voltage_rating
        )

        def make_dcsu_functionality(
            hd=hardware,
            tol=tolerance,
            sv=power_generation.ssu.regulate_voltage,
            vr=voltage_rating,
        ): 
            # if hd < tol:
            #     return 0
            # else: 
            #     if sv == vr:
            #         return 1.0  
            #     else: 
            #         return 0.0
            return 1.0

        dcsu_functionality = make_functionality(
            *dcsu_functionality_inputs,
            name="dcsu_functionality",
            functionality_func=make_dcsu_functionality
        )

        operational_mode = Variable(
            name="operational_mode",
            value=0
        )

        battery_power_in = Variable(
            name="battery_power_in",
            value=0.0
        )

        battery_power_demand = Variable(
            name="battery_power_demand",
            value=0.0
        ) 

        @make_function(operational_mode)
        def calc_operational_mode(
            s = sensor.measured_input,
            m = min_power_req,
        ):
            if s > m:
                return 1
            elif s < m:
                return -1
            
        @make_function(battery_power_in) 
        def calc_battery_power_in(
            s = power_generation.array.generate_power,
            o = operational_mode,
            pd = power_demands,
            df = dcsu_functionality,
            nbatt = number_of_batteries,
        ):
            if o == 1 and df == 1.0:
                return (s - pd)/nbatt
            else: 
                return 0
   
        @make_function(battery_power_demand)
        def calc_battery_power_demand(
            o = operational_mode,
            pd = power_demands,
            df = dcsu_functionality,
            nbatt = number_of_batteries,
        ):
            if o == -1 and df == 1.0:
                return pd/nbatt
            else: 
                return 0
        
    return dcsu