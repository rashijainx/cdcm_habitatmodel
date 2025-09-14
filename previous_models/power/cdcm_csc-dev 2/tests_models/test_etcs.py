"""
Testing ETCS Integration 

Author: 
    Rashi Jain 

Date: 
    09/10/2023 

"""

from cdcm import *
from cdcm_csc import *
from cdcm_csc_systems import *

from etcs.cold_plate import make_cold_plate 
from etcs.controller import make_controller 
from etcs.heater import make_heater 
from etcs.plumbing import make_plumbing
from etcs.radiator_panel import make_radiator_panel 
from etcs.tank import make_tank 
from etcs.valve import make_valve 

from power.switch import make_switch 

import datetime
import matplotlib.pyplot as plt

starting_epoch = datetime.datetime(2022, 1, 1)
time_steps = 709

if __name__ == "__main__":

    with System(name="etcs") as etcs:

        clock = make_clock(dt=1, units="hours")
        ext_env = SolarIrradiance("ext_env", clock, starting_epoch, time_steps)

        # switch_age_rate = Parameter(name="switch_age_rate", value=1.0/(24*365))
        # valve_age_rate = Parameter(name="valve_age_rate", value=1.0/(24*365))

        # plumbing_age_rate = Parameter(name="plumbing_age_rate", value=1.0/(24*365))
        # tank_age_rate = Parameter(name="tank_age_rate", value=1.0/(24*365))
        
        actuator_age_rate = Parameter(name="actuator_age_rate", value=1.0/(24*365))
        actuator_eccentric_amplitude = Parameter(name="actuator_eccentric_amplitude", value=0.1)

        panels_age_rate = Parameter(name="panels_age_rate", value=1.0/(24*365)) 
        
        external_dust_rate = Parameter(name="external_dust_rate", value=5.0 / (24 * 365))  
        # external_meteorite_impact = Parameter(name="external_meteorite_impact", value=0.1)  

        # sV2NH3T = make_switch(
        #     "sV2NH3T", 
        #     clock, 
        #     switch_age_rate, 
        # )

        # NH3_plumbing_supply = make_plumbing(
        #     "NH3_plumbing_supply",
        #     clock,
        #     plumbing_age_rate,
        #     external_dust_rate,
        #     external_meteorite_impact,
        # ) 

        # valve2NH3T = make_valve(
        #     "valve2NH3T",
        #     clock, 
        #     sV2NH3T, 
        #     NH3_plumbing_supply, 
        #     valve_age_rate, 
        # )

        # NH3_tank = make_tank(
        #     clock,
        #     tank_age_rate,
        #     external_dust_rate, 
        #     external_meteorite_impact, 
        #     valve2NH3T,
        # )

        # sVFNH3T = make_switch(
        #     "sVFNH3T", 
        #     clock, 
        #     switch_age_rate, 
        # )

        # valveFNH3T = make_valve(
        #     "valveFNH3T",
        #     clock, 
        #     sVFNH3T, 
        #     NH3_tank, 
        #     valve_age_rate, 
        # )

        # NH3_plumbing_out = make_plumbing(
        #     "NH3_plumbing_out",
        #     clock,
        #     plumbing_age_rate,
        #     external_dust_rate,
        #     external_meteorite_impact,
        #     sysIN=valveFNH3T,
        # ) 

        controller = make_controller(
            clock,
            actuator_age_rate,
            actuator_eccentric_amplitude,
            external_dust_rate,
            # external_meteorite_impact,
        )

        radiator_panel = make_radiator_panel(
            clock,
            panels_age_rate,
            external_dust_rate,
            # external_meteorite_impact,
            ext_env.solar_irradiance,
            controller,
        )

    file_name = __file__.split("/")[-1][:-3]

    etcs.forward()
    # print(f">.. {etcs.name} models runs forward..")

    # print(">.. fluid is supplied to the tank") 
    # print(NH3_plumbing_supply)
    # print(">.. fluid is stored in the tank") 
    # print(NH3_tank)
    # print(">.. fluid out from the tank") 
    # print(NH3_plumbing_out) 

    # print(">.. controller that orients radiator panel")
    # print(controller)
    # print(">.. radiator panel loses heat to external surroundings")
    # print(radiator_panel)
    


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