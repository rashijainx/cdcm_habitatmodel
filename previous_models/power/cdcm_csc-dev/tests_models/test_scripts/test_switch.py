"""Test model for switch 

Author:
    Rashi Jain
    
Date:
    09.10.2023 

    
"""

from cdcm import *
from cdcm_csc import make_pyvis_graph

from power.switch import make_switch


clock = make_clock(dt=1.0)

switch_age_rate = Parameter(
    name="switch_age_rate", value=1.0/(24*365)
)

sVTNH32P = make_switch(
    "sVTHNH32P", 
    clock, 
    switch_age_rate, 
)

print(sVTNH32P)
sVTNH32P.forward()

g = make_pyvis_graph(sVTNH32P)
try:
    g.show("test_switch.html", notebook=False)
except:
    g.show("test_switch.html")

   
    