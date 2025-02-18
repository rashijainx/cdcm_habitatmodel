import matplotlib.pyplot as plt
import datetime

from cdcm import *
from cdcm_utils import *
from cdcm_abstractions import *

from structure import *
from power_components import *

starting_epoch = datetime.datetime(2025, 1, 19)
time_steps = 5000


time_steps = 5000

if __name__ == "__main__":

    with System(name="system") as system:

        clock = make_clock(dt=1.0, units="hours")

        sun = SolarIrradiance("sun", clock, starting_epoch, time_steps)
        # moon = get_surface("moon", sun.solar_irradiance, 0.11)

        temperature = Variable(name="temperature", value=20.0)

        solar_array_age_rate = Variable(name="solar_array_age_rate", value=0.01/(24*365))
        number_of_panels = Variable(name="number_of_panels", value=10.0)
        panel_capacity = Variable(name="panel_capacity", value=50.0)
        operational_status = Variable(name="operational_status", value=1)

        solar_array = make_solar_array(
            "solar_array",
            clock,
            sun.solar_irradiance,
            solar_array_age_rate,
            (-20, 120),
            (0, 80),
            temperature,
            number_of_panels,
            panel_capacity, 
            operational_status,
        )

        wiring_inputs = (0.01/(24*365), 0.75)
        ssu_age_rate = Variable(name="ssu_age_rate", value=0.01/(24*365))
        ssu_voltage_rating = Variable(name="ssu_voltage_rating", value=160.0)
        ssu_threshold = (0.75, 50000.)

        ssu = make_ssu(
            "ssu",
            clock, 
            ssu_age_rate, 
            (0, 45),
            (20, 30),
            ssu_voltage_rating, 
            ssu_threshold,
            temperature, 
            wiring_inputs, 
            solar_array,
        )

        wiring = make_connection_wiring(
            "wiring", 
            clock, 
            0.01/(24*365),
            (0.75, 120),
            ssu
        )


    file_name = __file__.split("/")[-1][:-3]

    system.forward()
    print(system)

    print(">.. Pyvis is making the HTML file.")

    sys_graph = make_pyvis_graph(system)
    try:
        sys_graph.show(file_name + ".html", notebook=False)
    except:
        sys_graph.show(file_name + ".html")
    print(">... done")

    saver = SimulationSaver(file_name + ".h5",
                            system,
                            max_steps=time_steps,
                            overwrite=True
    )

    model = Simulator(system)

    for i in range(time_steps):
        model.forward()
        saver.save()
        model.transition()

    _map = {

        
    }

    data = extract_data_from_saver(saver, _map)

