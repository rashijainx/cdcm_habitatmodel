import matplotlib.pyplot as plt

from cdcm import *
from cdcm_utils import *
from cdcm_abstractions import *

from power_components import *

time_steps = 5000

if __name__ == "__main__":

    with System(name="system") as system:

        clock = make_clock(dt=1.0, units="hours")

        bcdu_age_rate = Variable(name="bcdu_age_rate", value=0.01/(24*365))
        external_temperature = Variable(name="external_temperature", value=25.0)
        
        battery = make_bcdu(
            "bcdu",
            clock,
            bcdu_age_rate,
            (0, 45),
            (20, 30),
            external_temperature,
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

        # BCDU
        "charge": "/system/bcdu/charge_battery",
        "discharge": "/system/bcdu/discharge_battery",
    }

    data = extract_data_from_saver(saver, _map)

    fig, axs = plt.subplots(nrows=2)

    axs[0].plot(data["t"], data["charge"])
    axs[0].set(ylabel="Charge")

    axs[1].plot(data["t"], data["discharge"])
    axs[1].set(ylabel="Discharge")

    plt.show()
    print("~~ovn!")
