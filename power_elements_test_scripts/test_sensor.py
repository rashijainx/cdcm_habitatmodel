import matplotlib.pyplot as plt
import datetime

from cdcm import *
from cdcm_utils import *
from cdcm_abstractions import *

from structure import *
from command_and_control_components import *

starting_epoch = datetime.datetime(2025, 1, 24)
time_steps = 1000
if __name__ == "__main__":

    with System(name="system") as system:

        clock = make_clock(dt=1.0, units="hours")
        sun = SolarIrradiance("sun", clock, starting_epoch, time_steps)
        
        sensor_age_rate = Variable(name="sensor_age_rate", value=0.01/(24*365))
        get_surface = Variable(name="external_temperature", value=25)
        noise = Variable(name="noise", value=50)

        sensor = make_sensor(
            "sensor",
            clock,
            sensor_age_rate,
            (-20, 120),
            (0, 80),
            get_surface,
            sun.solar_irradiance, 
            noise
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
    # model.add_event(2500, change_value(operational_status, 0))
    # model.add_event(3500, change_value(charging_status, 1))

    for i in range(time_steps):
        model.forward()
        saver.save()
        model.transition()

    _map = {
        "t": "/system/clock/t",
        "solar": "/system/sun/solar_irradiance",

        "measured": "/system/sensor/measured_input",
        "error": "/system/sensor/error",
    }

    data = extract_data_from_saver(saver, _map)

    fig, axs = plt.subplots(nrows=5)

    axs[0].plot(data["t"], data["solar"])
    axs[0].set(ylabel="Solar", title="sun")

    axs[1].plot(data["t"], data["measured"])
    axs[1].set(ylabel="Measured")

    axs[2].plot(data["t"], data["error"])
    axs[2].set(ylabel="Error")


    plt.show()
    print("~~ovn!")

    