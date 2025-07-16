# Sensor
from cdcm import * 
from cdcm_abstractions import *

import random

from common_constructs import *

__all__ = ["make_sensor"]

def make_sensor(
    name: str,
    clock: System,
    temperature: Variable,
    age_parameters: tuple, 
    operating_temperatures: tuple,
    surviving_temperatures: tuple,
    sensor_parameters: tuple,
    input: Variable
): 
    with System(name=name) as sensor:

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

        sensor_functionality_inputs = (
            aging.hardware,
            tolerance,
        )

        def make_sensor_functionality(
            hd=aging.hardware,
            tol=tolerance,
        ):
            if hd > tol: 
                return 1.0
            elif hd < tol and hd > (1 - tol): 
                return hd
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
    
        drift = Parameter(name="drift", value=sensor_parameters[0])
        noise = Parameter(name="noise", value=sensor_parameters[1])

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
                return 0,0

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