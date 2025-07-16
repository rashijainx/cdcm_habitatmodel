import matplotlib.pyplot as plt

from cdcm import *
from cdcm_utils import *

from battery import make_battery

time_steps = 5000

if __name__ == "__main__":

    with System(name="system") as system:

        clock = make_clock(dt=1.0, units="hours")

        battery = make_battery(
            "battery",
            clock,
            0.01/(24*365),
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


    