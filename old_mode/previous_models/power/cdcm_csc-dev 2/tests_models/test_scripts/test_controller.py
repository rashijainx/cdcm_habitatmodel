"""Test model for controller

Author:
    Rashi Jain
    
Date:
    xx
    
"""


from cdcm import *
from cdcm_csc import make_pyvis_graph

from etcs.controller import make_controller


with System(name="etcs") as etcs:
    clock = make_clock(dt=1.0)

    actuator_age_rate = Parameter(
        name="actuator_age_rate", value=1.0 / (24 * 365)
    )  

    actuator_eccentric_amplitude = Parameter(
        name="actuator_eccentric_amplitude", value=0.25
    )  

    external_dust_rate = Parameter(
        name="external_dust_rate", value=5.0 / (24 * 365)
    ) 

    external_meteorite_impact = Parameter(
        name="external_meteorite_impact", value=0.1
    )

    controller = make_controller(
        clock,
        actuator_age_rate,
        actuator_eccentric_amplitude,
        external_dust_rate,
        external_meteorite_impact,
    )

print(etcs)
etcs.forward()

g = make_pyvis_graph(etcs)
try:
    g.show("test_controller.html", notebook=False)
except:
    g.show("test_controller.html")

   
    