"""Testing radiator panel 

Author: 
    Rashi Jain
    R Murali Krishnan

Date: 
    9/21/2023
    9/24/2023

"""


from cdcm import *
from cdcm_csc import *
from cdcm_csc_systems import *

from etcs.controller import make_controller
from etcs.radiator_panel import make_radiator_panel

import datetime
import matplotlib.pyplot as plt

starting_epoch = datetime.datetime(2000, 1, 12)
time_steps = 709


with System(name="etcs") as etcs:

    clock = make_clock(dt=1, units="hours")
    
    actuator_age_rate = Parameter(
        name="actuator_age_rate", 
        value=0.0
    )  
        
    actuator_eccentric_amplitude = Parameter(
        name="actuator_erractic_amplitude", 
        value=0.0
    )  
    
    panels_age_rate = Parameter(
        name="panels_age_rate", 
        value=0.0,
    ) 
    
    external_dust_rate = Parameter(
        name="external_dust_rate", 
        value=5.0 / (24 * 365)
    )  
    
    external_meteorite_impact = Parameter(
        name="external_meteorite_impact", 
        value=0.1
    )  

    ext_env = SolarIrradiance("ext_env", clock, starting_epoch, time_steps)

    controller = make_controller(
        clock,
        actuator_age_rate,
        actuator_eccentric_amplitude,
        external_dust_rate,
        external_meteorite_impact,
    )

    radiator_panel = make_radiator_panel(
        clock,
        panels_age_rate,
        external_dust_rate,
        external_meteorite_impact,
        controller,
        ext_env.solar_irradiance,
    )

file_name = __file__.split("/")[-1][:-3]

etcs.forward()
print(f">.. {etcs.name} models runs forward..")

print(">.. model of the controller in a human readable format")
print(controller)
print(">.. model of the radiator panel in a human readable format")
print(radiator_panel)


print(">.. Pyvis is making the HTML...")
etcs_graph = make_pyvis_graph(etcs)
try:
    etcs_graph.show(file_name + ".html", notebook=False)
except:
    etcs_graph.show(file_name + ".html")
print(">.. done")

# # Simulate for 709 hours.
# saver = SimulationSaver(file_name + ".h5", etcs, max_steps=time_steps, overwrite=True)
# model = Simulator(etcs)

# # Define your events here
# model.add_event(20, change_value(etcs.external_dust_rate, 20*etcs.external_dust_rate.value))
# model.add_event(75, change_value(etcs.external_dust_rate, etcs.external_dust_rate.value))
# model.add_event(600, switch_binary_value(controller.actuator_power.health))

# for i in range(time_steps):
#     model.forward()
#     saver.save()
#     model.transition()

