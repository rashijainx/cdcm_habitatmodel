import matplotlib.pyplot as plt
import datetime

from cdcm import *
from cdcm_utils import *
from cdcm_abstractions import *

from structure import *
from power_components import *

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
        # sun.solar_irradiance = sun.solar_irradiance.value/max(sun.solar_irradiance.value)
        solar_array_age_rate = Variable(name="solar_array_age_rate", value=0.01/(24*365))

        number_of_panels = Variable(name="number_of_panels", value=10.0)
        panel_capacity = Variable(name="panel_capacity", value=50.0)
        operational_status = Variable(name="operational_status", value=1)

        # solar_array = make_solar_array(
        #     "solar_array",
        #     clock,
        #     sun.solar_irradiance,
        #     solar_array_age_rate,
        #     (-20, 120),
        #     (0, 80),
        #     get_surface,
        #     number_of_panels,
        #     panel_capacity, 
        #     operational_status,
        # )

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
        "t": "/system/clock/t",
        "solar": "/system/sun/solar_irradiance",
        "gcapacity": "/system/solar_array/generative_capacity",
        "solar_power": "/system/solar_array/generate_power",
    }

    data = extract_data_from_saver(saver, _map)

    fig, axs = plt.subplots(nrows=3)

    axs[0].plot(data["t"], data["solar"])
    axs[0].set(ylabel="Irraidance", title="Solar Array")

    axs[1].plot(data["t"], data["gcapacity"])
    axs[1].set(ylabel="Capacity", xlabel="Time")

    axs[2].plot(data["t"], data["solar_power"])
    axs[2].set(ylabel="Power")

    plt.show()
    print("~~ovn!")


    