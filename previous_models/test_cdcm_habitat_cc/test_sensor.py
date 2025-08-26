""" Unit Testing: Sensor

Author:
    Rashi Jain

Date:
    2/12/2024 | Unit testings + Integration
    2/26/2024 | Pep-8
"""
import sys
import datetime
import matplotlib.pyplot as plt

from cdcm_constructs import *
from cdcm_habitat import *

from cdcm import *
from cdcm_utils import extract_data_from_saver
from cdcm_utils import make_pyvis_graph

# Mathematical and Visualization Tools
import numpy as np
import matplotlib.pyplot as plt

starting_epoch = datetime.datetime(2024, 1, 19)
time_steps = 5000

# SENSOR
if __name__ == "__main__":

    with System(name="system") as system:

        clock = make_clock(dt=1.0, units="hours")

        battery_age_rate = 0.01/(365*24)

        battery = make_battery(
            "battery",
            clock,
            battery_age_rate
        )

        sensor_age_rate = 0.0075/(24*365)
        sensor_power_threshold = 0.5
        sensor_drift_behavior = 0.0
        sensor_random_behavior = 0.005

        sensor = make_sensor(
            "sensor",
            clock,
            sensor_age_rate,
            sensor_power_threshold,
            sensor_drift_behavior,
            sensor_random_behavior,
            battery,
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

    # # Define Events Here  - Battery
    # model.add_event(3500, change_value(system.battery.age_rate, 1))

    # # Define Events Here - Sensor
    # model.add_event(1250, change_value(system.sensor.drift_behavior, 0.125))

    for i in range(time_steps):
        model.forward()
        saver.save()
        model.transition()

    _map = {
        "t": "/system/clock/t",

        "hardware_health": "/system/sensor/hardware/functionality",
        "functionality": "/system/sensor/sense_source",
        }

    data = extract_data_from_saver(saver, _map)

    fig, axs = plt.subplots(nrows=2)

    axs[0].plot(data["t"], data["functionality"])
    axs[0].set(ylabel="Functionality", title="sensor")

    axs[1].plot(data["t"], data["hardware_health"])
    axs[1].set(xlabel="Time (hrs)", ylabel="Health")

    plt.show()
    print("~~ovn!")
