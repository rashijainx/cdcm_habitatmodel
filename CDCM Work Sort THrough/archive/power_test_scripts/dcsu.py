from cdcm import *
from cdcm_abstractions import *

from common_constructs import * 
from sensor import *
from wiring import *


__all__ = [
    "make_dcsu",
    "make_mbsu"
    
]

def make_dcsu(
    name: str,
    clock: System,
    solar_irradiance: Variable,
    temperature: Variable,
    age_parameters: tuple,
    operating_temperatures: tuple,
    surviving_temperatures: tuple,
    batteries: float,
    minimum_power_required: float,
    power_demand: Variable,
    sensor_parameters: tuple,
    wiring_parameters: tuple,
    power_generator: System,
) -> System:

    with System(name=name) as dcsu:

        aging = make_aging_component(
            "aging",
            clock,
            age_parameters,
            operating_temperatures,
            surviving_temperatures,
            temperature,
        )

        sensor = make_sensor(
            "sensor",
            clock, 
            temperature,
            (sensor_parameters[0], sensor_parameters[1], sensor_parameters[2]),
            (sensor_parameters[3], sensor_parameters[4]),
            (sensor_parameters[5], sensor_parameters[6]),
            (sensor_parameters[7], sensor_parameters[8]),
            solar_irradiance
        )

        wiring = make_wiring(
            "wiring",
            clock,
            wiring_parameters,
        )

        tolerance = Variable(
            name="tolerance",
            value=age_parameters[2]
        )

        dcsu_functionality_inputs = (
            aging.hardware,
            tolerance,
            wiring.transfer_electricity,
        )

        def make_dcsu_functionality(
            hd=aging.hardware,
            tol=tolerance,
            w = wiring.transfer_electricity,
        ): 
            if hd > tol and w == 1.0:
                return 1.0
            else: 
                return 0.0

        dcsu_functionality = make_functionality(
            *dcsu_functionality_inputs,
            name="distribute_power",
            functionality_func=make_dcsu_functionality
        )

        min_power_threshold = Variable(
            name="min_power_threshold",
            value=minimum_power_required
        )

        number_of_batteries = Variable(
            name="number_of_batteries",
            value=batteries
        )
    
        operational_mode = Variable(
            name="operational_mode",
            value=0
        )

        @make_function(operational_mode)
        def calc_operational_mode(
            s = sensor.measured_input,
            m = min_power_threshold,
            health = dcsu_functionality,
            num_batt = number_of_batteries,
        ):
            if health == 1.0: 
                if s > m and num_batt > 0:
                    return 1
                elif s < m and num_batt > 0:
                    return -1
                elif s > m and num_batt == 0: 
                    return 0.5
                elif s < m and num_batt == 0: 
                    return 0
            else:
                return 0.0
        
        battery_power_change = Variable(
            name="battery_power_change",
            value=0.0
        )

        @make_function(battery_power_change)
        def calc_battery_power_change(
            health = dcsu_functionality,
            mode = operational_mode,
            pg = power_generator.generate_power,
            pd = power_demand,
            m = min_power_threshold,
            num_batt = number_of_batteries,
        ):
            if mode == 1 or mode == -1 and health == 1.0: 
                return abs(pg - (pd - m))/num_batt
            else:
                return 0.0
            
        downstream_load = Variable(
            name="downstream_load",
            value=0.0
        )

        @make_function(downstream_load)
        def calc_downstream_load(
            p = power_generator.generate_power,
            pd = power_demand,
            mode = operational_mode,
            health = dcsu_functionality,
        ):
            if mode == 1 or mode == -1 and health == 1.0:
                if pd > p: 
                    return p
                else: 
                    return pd
            elif mode == 0.5 and health == 1.0:
                if pd > p: 
                    return p
                else: 
                    return pd
            else: 
                return 0.0
        
        
        
    return dcsu


def make_mbsu(
    name: str,
    clock: System,
    temperature: Variable,
    age_parameters: tuple,
    operating_temperatures: tuple,
    surviving_temperatures: tuple,
    minimum_power_required: float,
    downstream_loads: tuple,
    wiring_parameters: tuple,
    main_distributor: System,
) -> System:

    with System(name=name) as mbsu:

        aging = make_aging_component(
            "aging",
            clock,
            age_parameters,
            operating_temperatures,
            surviving_temperatures,
            temperature,
        )

        wiring = make_wiring(
            "wiring",
            clock,
            wiring_parameters,
        )

        tolerance = Variable(
            name="tolerance",
            value=age_parameters[2]
        )

        mbsu_functionality_inputs = (
            aging.hardware,
            tolerance,
            wiring.transfer_electricity,
        )

        def make_mbsu_functionality(
            hd=aging.hardware,
            tol=tolerance,
        ): 
            if hd > tol:
                return 1.0
            else: 
                return 0.0

        mbsu_functionality = make_functionality(
            *mbsu_functionality_inputs,
            functionality_func=make_mbsu_functionality
        )

        min_power_threshold = Variable(
            name="min_power_threshold",
            value=minimum_power_required
        )
    

        # operational_mode = Variable(
        #     name="operational_mode",
        #     value=0
        # )

        # battery_power_change = Variable(
        #     name="battery_power_change",
        #     value=0.0
        # )

        # @make_function(battery_power_change)
        # def calc_battery_power_change(
        #     health = dcsu_functionality,
        #     mode = operational_mode,
        #     pg = power_generator.generate_power,
        #     pd = power_demand,
        #     m = min_power_threshold,
        #     num_batt = number_of_batteries,
        # ):
        #     if mode == 1 or mode == -1 and health == 1.0: 
        #         return abs(pg - (pd - m))/num_batt
        #     else:
        #         return 0.0
            
        # downstream_load = Variable(
        #     name="downstream_load",
        #     value=0.0
        # )

        # @make_function(downstream_load)
        # def calc_downstream_load(
        #     p = power_generator.generate_power,
        #     pd = power_demand,
        #     mode = operational_mode,
        #     health = dcsu_functionality,
        # ):
        #     if mode == 1 or mode == -1 and health == 1.0:
        #         if pd > p: 
        #             return p
        #         else: 
        #             return pd
        #     elif mode == 0.5 and health == 1.0:
        #         if pd > p: 
        #             return p
        #         else: 
        #             return pd
        #     else: 
        #         return 0.0
        
        
        
    return mbsu