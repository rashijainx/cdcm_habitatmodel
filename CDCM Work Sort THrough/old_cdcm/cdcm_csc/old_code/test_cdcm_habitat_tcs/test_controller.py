""" Integrated Testing: Controller

Author:
    Rashi Jain

Date:
    2/14/2024 | Unit testings + Integration
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

# CONTROLLER
if __name__ == "__main__":

    with System(name="system") as system:

        clock = make_clock(dt=1.0, units="hours")

        battery_age_rate = 0.01/(365*24)

        controller_age_rate = 0.001/(24*365)
        controller_interact_variable = 0.0
        controller_mechanism_failure = 0.0
        power = 1
        controller_power_threshold = 0.5

        controller = make_controller(
            "controller",
            clock,
            controller_age_rate,
            controller_interact_variable,
            controller_mechanism_failure,
            power,
            controller_power_threshold,
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

    saver = SimulationSaver(
        file_name + ".h5",
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
        "t": "/system/clock/t",

        # Controllers
        "controller_functionality": "/system/controller/rotate_component"
        }

    data = extract_data_from_saver(saver, _map)

    # Controller
    fig, axs = plt.subplots(nrows=2)

    axs[0].plot(data["t"], data["controller_functionality"])
    axs[0].set(ylabel="Functionality", title="controller")

    plt.show()
    print("~~ovn!")
