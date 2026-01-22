"""Test a system of components

Author:
    R Murali Krishnan
    
Date:
    09.19.2023

"""

from cdcm import *
from cdcm_csc import *

import numpy as np


handling_rate = 0.1
radiation_rate = 0.1

with System(name="sys") as sys:

    clock = make_clock(dt=1.0)


    handling = HealthVariable(name="handling", value=1.0)

    radiation = HealthVariable(name="radiation", value=1.0)
    @make_function(radiation)
    def fn_calculate_radiation(t=clock.t):
        return np.sin(t)
    
    sensor_damage_rate = HealthVariable(name="sensor_damage_rate", value=0.0)
    @make_function(sensor_damage_rate)
    def calculate_sensor_damage_rate(handling=handling, radiation=radiation):
        return handling * handling_rate + radiation * radiation_rate
    
    dust = HealthVariable(name="dust", value=0.0)
    @make_function(dust)
    def fn_calculate_dust_rate(t=clock.t):
        return np.sin(t)



    with System(name="fdd") as fdd:

        # Component by default assumes health variable
        hardware = make_component("hardware", nominal_health=2.0)
        
        # Component with a binary valued health variable
        algorithm = make_component("algorithm", nominal_health=1)

        # Component with a continuously time-varying health state
        power_bus = make_component("power_bus", 
                                   dt=clock.dt,
                                   nominal_health=1.0,
                                   health_damage_rate=1.0/(24*365))

        sensor = make_component("sensor",
                                dt=clock.dt,
                                health_damage_rate=sensor_damage_rate)
        
        # Component with an aging behavior
        input_terminal = make_component("input_terminal",
                                        dt=clock.dt,
                                        aging_rate=0.1/(24*365),
                                        aging_func=linear_function())
        
        output_terminal = make_component("output_terminal",
                                   dt=clock.dt,
                                   health_damage_rate=dust,
                                   aging_rate=0.1/(24*365),
                                   aging_func=linear_function())
        
        wire_aging_rate = HealthVariable(name="wire_aging_rate", value=0.0)
        @make_function(wire_aging_rate)
        def fn_wire_aging_rate(x1=hardware.health, x2=input_terminal.age, x3=output_terminal.age):
            """Aging rat of the wires of the FDD"""
            return x1 * x2
        
        wires = make_component("wires",
                               dt=clock.dt,
                               aging_rate=wire_aging_rate,
                               aging_func=linear_function())
        

        
        functionality = make_functionality(hardware, algorithm, power_bus, input_terminal, output_terminal, wires)
                                   



print(fdd)

sys.forward()