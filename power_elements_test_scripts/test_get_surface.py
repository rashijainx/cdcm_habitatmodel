import matplotlib.pyplot as plt
import datetime

from cdcm import *
from cdcm_utils import *
from cdcm_abstractions import *

from structure import *

starting_epoch = datetime.datetime(2025, 1, 19)
time_steps = 5000

if __name__ == "__main__":

    with System(name="system") as system:

        clock = make_clock(dt=1.0, units="hours")
        sun = SolarIrradiance("sun", clock, starting_epoch, time_steps)
        
        albedo = Variable(name="albedo", value=0.11)
        surface = get_surface(
            "surface", 
            sun.solar_irradiance,
            albedo,
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
    # model.add_event(2500, change_value(external_temperature, 35.0))
    # model.add_event(500, change_value(operational_status, 0))
    # model.add_event(1500, change_value(operational_status, 1))

    for i in range(time_steps):
        model.forward()
        saver.save()
        model.transition()

    _map = {
  
    }

    data = extract_data_from_saver(saver, _map)

    