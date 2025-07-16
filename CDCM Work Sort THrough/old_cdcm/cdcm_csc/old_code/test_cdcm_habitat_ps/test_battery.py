""" Unit Testing: Battery

Author:
    Rashi Jain

Date:
    2/12/2024 | Unit testings + Integration
    2/19/2024 | Follows Pep-8
"""

import datetime
import matplotlib.pyplot as plt

from cdcm_constructs import *
from cdcm_habitat import *

from cdcm import *
from cdcm_utils import extract_data_from_saver
from cdcm_utils import make_pyvis_graph

starting_epoch = datetime.datetime(2024, 1, 19)
time_steps = 5000

# BATTERY
if __name__ == "__main__":

    with System(name="system") as system:

        clock = make_clock(dt=1.0, units="hours")

        age_rate = 0.01/(24*365)

        battery = make_battery(
            "battery",
            clock,
            age_rate
        )

    file_name = __file__.split("/")[-1][:-3]

    system.forward()
    print(system)

    print(">.. Pyvis is making the HTML file.")

    tcs_graph = make_pyvis_graph(system)
    try:
        tcs_graph.show(file_name + ".html", notebook=False)
    except:
        tcs_graph.show(file_name + ".html")
    print(">... done")

    saver = SimulationSaver(file_name + ".h5",
                            system,
                            max_steps=time_steps,
                            overwrite=True
                            )

    model = Simulator(system)

    # Define Events Here
    model.add_event(35000, change_value(system.battery.age_rate, 1))

    for i in range(time_steps):
        model.forward()
        saver.save()
        model.transition()

    _map = {
        "t": "/system/clock/t",

        # Batteries
        "hardware_health": "/system/battery/hardware/functionality",
        "functionality": "/system/battery/generate_power",
        }

    data = extract_data_from_saver(saver, _map)

    fig, axs = plt.subplots(nrows=2)

    axs[0].plot(data["t"], data["functionality"])
    axs[0].set(ylabel="Power", title="battery")

    axs[1].plot(data["t"], data["hardware_health"])
    axs[1].set(xlabel="Time (hrs)", ylabel="Health")

    plt.show()
    print("~~ovn!")
