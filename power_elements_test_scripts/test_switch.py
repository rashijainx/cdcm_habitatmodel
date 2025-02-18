import matplotlib.pyplot as plt

from cdcm import *
from cdcm_utils import *
from cdcm_abstractions import *

from power_consumer import make_power_consumer
from switch import make_fuse, make_switch

time_steps = 5000

if __name__ == "__main__":

    with System(name="system") as system:

        clock = make_clock(dt=1.0, units="hours")

        vacuum_aging_rate = 0.01/(24*365)
        vaccum_operational_status = 1, 
        vacuum_voltage_rating = 120
    
        aging_rate = 0.01/(24*365)
        voltage = Variable(name="voltage", value=120.0)

        fuse = make_fuse(
            "fuse",
            clock,
            aging_rate,
            voltage,
            (1, 120)
        )

        switch = make_switch(
            "switch",
            clock,
            aging_rate,
            fuse
        )

        vacuum_cleaner = make_power_consumer(
            "vacuum_cleaner",
            clock,
            vacuum_aging_rate,
            switch,
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

