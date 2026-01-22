
from cdcm import *
from cdcm_csc import *
from cdcm_csc_systems import *

from etcs.controller import make_controller
from etcs.radiator_panel import make_radiator_panel
from etcs.ammonia import make_ammonia

import datetime
import matplotlib.pyplot as plt

starting_epoch = datetime.datetime(2000, 1, 12)
time_steps = 709

if __name__ == "__main__":

    with System(name="etcs") as etcs:

        clock = make_clock(dt=1, units="hours")
        # Age 1%/ year
        actuator_age_rate = Parameter(
            name="actuator_age_rate", 
            value=0.0
        )  
        # Amplitude 0.25 
        actuator_eccentric_amplitude = Parameter(
            name="actuator_erractic_amplitude", 
            value=0.0
        )  
        # Age 1%/ year
        panels_age_rate = Parameter(
            name="panels_age_rate", 
            value=0.0,
        ) 
        # Dust 1%/ year 
        external_dust_rate = Parameter(
            name="external_dust_rate", 
            value=5.0 / (24 * 365)
        )  
        # Meteorite Impact
        external_meteorite_impact = Parameter(
            name="external_meteorite_impact", 
            value=0.0
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

        ammonia = make_ammonia(
            clock, 
            external_dust_rate, 
            radiator_panel, 
            ext_env.solar_irradiance)

    etcs.forward()

    saver = SimulationSaver("test_ammonia.h5", etcs, max_steps=time_steps, overwrite=True)
    model = Simulator(etcs)

    for i in range(time_steps):
        model.forward()
        saver.save()
        model.transition()
    
    g = make_pyvis_graph(ammonia)
    try:
        g.show("ammonia.html", notebook=False)
    except:
        g.show("ammonia.html")

    fig,ax = plt.subplots(nrows=2, ncols=2)

    ax[0, 0].plot(saver.file_handler["/etcs/clock/t"][:], saver.file_handler["/etcs/ammonia/ammonia_functionality"][:])
    
    ax[0, 1].plot(saver.file_handler["/etcs/clock/t"][:], saver.file_handler["/etcs/ammonia/temperature/functionality"][:])

    ax[1, 0].plot(saver.file_handler["/etcs/clock/t"][:], saver.file_handler["/etcs/ext_env/solar_irradiance"][:])
    plt.show()