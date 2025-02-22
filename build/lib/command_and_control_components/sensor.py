# Sensor
from cdcm import * 
from cdcm_abstractions import *

import random

__all__ = ["make_sensor"]

def make_sensor(
    name: str,
    clock: System,
    input: Variable,
    age_parameters: tuple, 
    sensor_parameters: tuple,
): 
    with System(name=name) as sensor:

        hardware = make_component(
            name="hardware",
            health_damage_rate=age_parameters[0],
            dt=clock.dt,
            Ed=1.0
        )
        
        tolerance = age_parameters[1]

        sensor_functionality_inputs = (
            hardware, 
            tolerance,
        )
        def make_sensor_functionality(
            hardware=hardware,
            tolerance=tolerance,
        ):
            if hardware > tolerance:
                return hardware
            else:
                return 0
    
        truncated_name = name.split("_")[0]
        sensor_functionality = make_functionality(
            *sensor_functionality_inputs,
            name="sense_" + truncated_name,
            functionality_func=make_sensor_functionality
        )

        measured_input = Variable(
            name = "measured_input",
            value = input
        )

        drift = sensor_parameters[0]
        noise = sensor_parameters[1]

        @make_function(measured_input)
        def calc_measure_input(
            i = input,
            d = drift,
            n = noise,
            health = sensor_functionality,
        ):
            if health > 0: 
                return i + d*random.uniform(-n, n)
            else: 
                return 0

        error = Variable(
            name = "error",
            value = 0.0
        )

        @make_function(error)
        def calc_error(
            m = measured_input, 
            i = input, 
        ): 
            return abs(m - i)
    return sensor 