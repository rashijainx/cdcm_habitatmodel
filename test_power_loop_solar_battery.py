import matplotlib.pyplot as plt
import datetime

from cdcm import *
from cdcm_utils import *
from cdcm_abstractions import *

from structure import *
from power_components import *

starting_epoch = datetime.datetime(2025, 1, 19)
time_steps = 708

if __name__ == "__main__":
    with System(name="system") as system:

        clock = make_clock(dt=1.0, units="hours")

        battery_age = Variable(name="battery_age", value=0.01/(24*365))
        battery_operating_temperature = (-100, 100)
        battery_survival_temperature = (-275, 275)
        maximum_capacity = Variable(name="maximum_capacity", value=100)
        dcsu_operational_mode = Variable(name="dcsu_operational_mode", value=0)

        dummy_temperature = Variable(name="dummy_temperature", value=20.0)


        bcdu_age = 0.01/(24*365); bcdu_tolerance = 0.5
        bcdu_age_parameters = (bcdu_age, bcdu_tolerance)
        bcdu_charge_rate = Variable(name="bcdu_charge_rate", value=0.01); bcdu_discharge_rate = Variable(name="bcdu_discharge_rate", value=0.01)
        bcdu_rates = (bcdu_charge_rate, bcdu_discharge_rate)
        # Operational Mode (Determined by DCSU) (1: Charging, 0: Not Charging, Not Discharging, -1: Discharging) 

        battery = make_integrated_battery(
            "battery",
            clock, 
            battery_age,
            battery_operating_temperature,
            battery_survival_temperature,
            dummy_temperature,
            maximum_capacity,
            dcsu_operational_mode,
            bcdu_age_parameters,
            bcdu_rates,
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
