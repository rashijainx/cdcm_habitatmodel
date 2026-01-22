""" Testing Tank Model

Author: 
    Darin Lin
    Rashi Jain
    
Date: 
    10/05/2023 
    10/09/2023 
    
"""

from cdcm import *
from cdcm_csc import *
from cdcm_csc_systems import *

from etcs.plumbing import *
from etcs.tank import *

import matplotlib.pyplot as plt

if __name__ == "__main__":

    with System(name="etcs") as etcs:

        clock = make_clock(dt=1, units="hours")

        tank_age_rate = Parameter(
            name="tank_age_rate", 
            value=1.0/(24*365)
        )

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

        plumbingIN = make_plumbing(
            "plumbingIN",
            clock,
            plumbing_age_rate,
            external_dust_rate,
            external_meteorite_impact,
        ) 

        plumbingOUT = make_plumbing(
            "plumbingOUT",
            clock,
            plumbing_age_rate,
            external_dust_rate,
            external_meteorite_impact,
        ) 

        tank = make_tank(
            clock,
            tank_age_rate,
            plumbingIN,
            plumbingOUT,
        )
      
    file_name = __file__.split("/")[-1][:-3]

    etcs.forward()
    print(f">.. {etcs.name} models runs forward..")

    print(">.. model of the plumbingIN in a human readable format")
    print(plumbingIN)
    # print(">.. model of the plumbingOUT in a human readable format")
    # print(plumbingOUT)
    print(">.. model of the tank in a human readable format")
    print(tank)


    print(">.. Pyvis is making the HTML...")
    etcs_graph = make_pyvis_graph(etcs)
    try:
        etcs_graph.show(file_name + ".html", notebook=False)
    except:
        etcs_graph.show(file_name + ".html")
    print(">.. done")


