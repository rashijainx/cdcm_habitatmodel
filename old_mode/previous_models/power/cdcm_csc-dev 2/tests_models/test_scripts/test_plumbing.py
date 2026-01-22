"""Testing plumbing 

Author: 
    Rashi Jain


Date: 
    10/06/2023 

"""


from cdcm import *
from cdcm_csc import *
from cdcm_csc_systems import *

from etcs.plumbing import * 


clock = make_clock(dt=1, units="hours")
        
plumbing_age_rate = Parameter(
    name="plumbing_age_rate", 
    value=1.0/(24*365)
)  
        
        
external_dust_rate = Parameter(
    name="external_dust_rate", 
    value=5.0 / (24 * 365)
)  
        
external_meteorite_impact = Parameter(
    name="external_meteorite_impact", 
    value=0.1
)  

plumbing = make_plumbing(
    "plumbing",
    clock,
    plumbing_age_rate,
    external_dust_rate,
    external_meteorite_impact,
    
)

print(plumbing)
plumbing.forward()

g = make_pyvis_graph(plumbing)
try:
    g.show("test_plumbing.html", notebook=False)
except:
    g.show("test_plumbing.html")
  
