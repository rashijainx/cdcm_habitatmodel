import matplotlib.pyplot as plt

from cdcm import *
from cdcm_utils import *
from cdcm_abstractions import *

from voltage_regulator import make_voltage_regulator

time_steps = 5000

if __name__ == "__main__":

    with System(name="system") as system:

        clock = make_clock(dt=1.0, units="hours")

        ssu_age_rate = Variable(name="ssu_age_rate", value=0.01/(24*365))
        ssu_voltage_rating = Variable(name="ssu_voltage_rating", value=160.0)
        ssu_threshold = Variable(name="ssu_threshold", value=0.75)
        external_temperature = Variable(name="external_temperature", value=25.0)
        initial_charge = Variable(name="initial_charge", value=100.0)

        ssu = make_voltage_regulator(
            "ssu",
            clock, 
            ssu_age_rate, 
            (0, 45),
            (20, 30),
            ssu_voltage_rating, 
            ssu_threshold,
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
    model.add_event(2500, change_value(ssu.age_rate, 0.5))

    for i in range(time_steps):
        model.forward()
        saver.save()
        model.transition()

    _map = {
        "t": "/system/clock/t",
        "temp": "/system/external_temperature",

        # SSU
        "age_rate": "/system/ssu/age_rate",
        "hardware_health": "/system/ssu/regulate_voltage",
        "voltage_out": "/system/ssu/voltage",
    }

    data = extract_data_from_saver(saver, _map)

    fig, axs = plt.subplots(nrows=5)

    axs[0].plot(data["t"], data["temp"])
    axs[0].set(ylabel="External Temp", title="non rechargeable battery")

    axs[1].plot(data["t"], data["age_rate"])
    axs[1].set(ylabel="Age Rate")

    axs[2].plot(data["t"], data["hardware_health"])
    axs[2].set(ylabel="Hardware Health")

    axs[3].plot(data["t"], data["voltage_out"])
    axs[3].set(ylabel="Voltage")

    plt.show()
    print("~~ovn!")


    