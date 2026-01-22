""" Testing cold plate

Author: 
    Rashi Jain 

Date: 
    10/06/2023

"""

from cdcm import * 
from cdcm_csc import * 
from cdcm_csc_systems import *  

from etcs.plumbing import *
from etcs.cold_plate import *

if __name__ == "__main__": 

    with System(name="cold_plate_assembly") as cold_plate_assembly: 

        clock = make_clock(dt = 1, units = "hours") 

        cold_plate_aging_rate = Parameter(
            name = "cold_plate_aging_rate", 
            value = 1.0/(24*365)
        ) 

        plumbing_aging_rate = Parameter(
            name = "plumbing_aging_rate", 
            value = 1.0/(24*365)
        ) 

        external_dust_rate = Parameter(
            name = "external_dust_rate", 
            value = 5.0/(24*365)
        )

        external_meteorite_impact = Parameter(
            name = "external_meteorite_impact", 
            value = 0.1
        )

        cold_plate_plumbing = make_plumbing(
            "cold_plate_plumbing",
            clock,
            plumbing_aging_rate,
            external_dust_rate,
            external_meteorite_impact,
        )

        cold_plate = make_cold_plate(
            clock,
            cold_plate_aging_rate,
            external_meteorite_impact,
            cold_plate_plumbing,
        )
        
    
    file_name = __file__.split("/")[-1][:-3]

    cold_plate_assembly.forward()
    print(f">.. {cold_plate_assembly.name} models runs forward..")

    print(">.. model of the controller in a human readable format")
    print(cold_plate_plumbing)
    print(">.. model of the radiator panel in a human readable format")
    print(cold_plate)


    print(">.. Pyvis is making the HTML...")
    cold_plate_graph = make_pyvis_graph(cold_plate_assembly)
    try:
        cold_plate_graph.show(file_name + ".html", notebook=False)
    except:
        cold_plate_graph.show(file_name + ".html")
    print(">.. done")

