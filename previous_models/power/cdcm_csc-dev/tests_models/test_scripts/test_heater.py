"""Testing Heater 

Author:
    Noah Colasanti
    Rashi Jain
    
Date: 
    10/3/2023 
    10/9/2023 
"""

from cdcm import *
from cdcm_csc import *

from etcs.heater import *

import matplotlib.pyplot as plt

clock = make_clock(dt=1.0)

heater_age_rate = Parameter(
    name="heater_age_rate", value=1.0 / (24 * 365)
)

heater_eccentric_amplitude = Parameter(
    name="heater_eccentric_amplitude", value=0.25
)

external_dust_rate = Parameter(
    name="external_dust_rate", value=5.0 / (24 * 365)
)
    
external_meteorite_impact = Parameter(
    name="external_meteorite_impact", value=0.5 / (24 * 365)
)

heater = make_heater(
    clock,
    heater_age_rate,
    heater_eccentric_amplitude, 
    external_dust_rate,
    external_meteorite_impact,
)

print(heater)
heater.forward()

g = make_pyvis_graph(heater)
try:
    g.show("test_heater.html", notebook=False)
except:
    g.show("test_heater.html")
