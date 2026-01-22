"""Testing valves

Author: 
    Rashi Jain
 
Date: 
    10/10/2023 

"""


from cdcm import *
from cdcm_csc import *
from cdcm_csc_systems import *

from etcs.valve import make_valve
from etcs.plumbing import make_plumbing
from power.switch import make_switch


if __name__ == "__main__":

    with System(name="etcs") as etcs:

        clock = make_clock(dt=1, units="hours")
        
        switch_age_rate = Parameter(
            name="switch_age_rate", 
            value=1.0/(24*365), 
        )  

        valve_age_rate = Parameter(
            name="valve_age_rate", 
            value=1.0/(24*365), 
        )

        plumbing_age_rate = Parameter( 
            name="plumbing_age_rate", 
            value=1.0/(24*365), 
        )
        external_dust_rate = Parameter(
            name="external_dust_rate", 
            value=5.0 / (24 * 365)
        )  
        
        external_meteorite_impact = Parameter(
            name="external_meteorite_impact", 
            value=0.1
        )  

        sVTNH32P = make_switch(
            "sVTHNH32P", 
            clock, 
            switch_age_rate, 
        )

        plumbing = make_plumbing(
            "plumbing", 
            clock, 
            plumbing_age_rate, 
            external_dust_rate, 
            external_meteorite_impact, 
        )

        valve = make_valve(
            "v1",
            clock, 
            sVTNH32P, 
            plumbing, 
            valve_age_rate,
        )

    file_name = __file__.split("/")[-1][:-3]

    etcs.forward()
    print(f">.. {etcs.name} models runs forward..")

    print(">.. model of the switch in a human readable format")
    print(sVTNH32P)
    print(">.. model of the valve in a human readable format")
    print(valve)


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