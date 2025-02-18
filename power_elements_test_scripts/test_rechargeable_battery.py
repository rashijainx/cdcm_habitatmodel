import matplotlib.pyplot as plt

from cdcm import *
from cdcm_utils import *
from cdcm_abstractions import *

from power_components import *

time_steps = 5000

if __name__ == "__main__":

    with System(name="system") as system:

        clock = make_clock(dt=1.0, units="hours")
        external_temperature = Variable(name="external_temperature", value=25.0)
        
        cs_age_rate = Variable(name="cs_age_rate", value=0.01/(24*365))
        tolerance = Variable(name="tolerance", value=0.75)
        charging_rate = Variable(name="charging_rate", value=0.01)

        charging_station = make_charging_station(
            "charging_station",
            clock,
            cs_age_rate,
            (0, 45),
            (20, 30),
            external_temperature,
            tolerance, 
            charging_rate,
        )

        battery_age_rate = Variable(name="battery_age_rate", value=0.01/(24*365))
        initial_charge = Variable(name="initial_charge", value=100.0)
        discharge_rate = Variable(name="discharge_rate", value=0.01)
        operational_status = Variable(name="operational_status", value=1)
        charging_status = Variable(name="charging_status", value=0)

        battery = make_rechargeable_battery(
            "battery",
            clock,
            battery_age_rate,
            (0, 45),
            (20, 30),
            initial_charge.value,
            external_temperature,
            discharge_rate,
            operational_status,
            charging_status,
            charging_station,
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
    model.add_event(2500, change_value(operational_status, 0))
    model.add_event(3500, change_value(charging_status, 1))

    for i in range(time_steps):
        model.forward()
        saver.save()
        model.transition()

    _map = {
        "t": "/system/clock/t",
        "temp": "/system/external_temperature",

        # Batteries
        "age_rate": "/system/battery/age_rate",
        "hardware_health": "/system/battery/hardware/functionality",
        "remaining_charge": "/system/battery/remaining_charge",
        "functionality": "/system/battery/provide_power",
    }

    data = extract_data_from_saver(saver, _map)

    fig, axs = plt.subplots(nrows=5)

    axs[0].plot(data["t"], data["temp"])
    axs[0].set(ylabel="External Temp", title="non rechargeable battery")

    axs[1].plot(data["t"], data["age_rate"])
    axs[1].set(ylabel="Age Rate")

    axs[2].plot(data["t"], data["hardware_health"])
    axs[2].set(ylabel="Hardware Health")

    axs[3].plot(data["t"], data["remaining_charge"])
    axs[3].set(ylabel="Remaining Charge")

    axs[4].plot(data["t"], data["functionality"])
    axs[4].set(xlabel="Time", ylabel="Functionality")

    plt.show()
    print("~~ovn!")
