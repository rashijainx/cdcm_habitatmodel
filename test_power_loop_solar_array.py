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

        sun = SolarIrradiance("sun", clock, starting_epoch, time_steps)
        albedo = Variable(name="albedo", value=0.11)

        surface = get_surface(
            "surface",
            sun.solar_irradiance,
            albedo,
        )

        dummy_temperature = Variable(name="dummy_temperature", value=20.0)

        # Input these variables from YAML file for Solar Array 
        solar_array_age = Variable(name="solar_array_age", value=0.01/(24*365))
        solar_array_operating_temperature = (-100, 100)
        solar_array_surviving_temperature = (-275, 275)
        number_of_panels = Variable(name="number_of_panels", value=10)
        panel_capacity = Variable(name="panel_capacity", value=50)
        solar_array_operational_status = Variable(name="operational_status", value=1) 

        # solar_array = make_solar_array(
        #     "solar_array",
        #     clock,
        #     sun.solar_irradiance,
        #     solar_array_age,
        #     solar_array_operating_temperature,
        #     solar_array_surviving_temperature,
        #     dummy_temperature,
        #     number_of_panels,
        #     panel_capacity,
        #     solar_array_operational_status,
        # )

        # Input these variables from YAML file for SSU 
        ssu_age = Variable(name="ssu_age", value=0.01/(24*365))
        ssu_operating_temperature = (-100, 100)
        ssu_surviving_temperature = (-275, 275)
        ssu_voltage_rating = Variable(name="ssu_voltage_rating", value=160.0)
        ssu_threshold = (0.75, 50000)
        ssu_wiring = (0.01/(24*365), 0.75)
    
        # solar_array_ssu = make_ssu(
        #     "solar_array_ssu",
        #     clock,
        #     ssu_age,
        #     ssu_operating_temperature,
        #     ssu_surviving_temperature,
        #     dummy_temperature,
        #     ssu_voltage_rating,
        #     ssu_threshold,
        #     ssu_wiring,
        #     solar_array,
        # )

        solar_array = make_integrated_array(
            "solar_assembly",
            clock,
            sun.solar_irradiance,
            (solar_array_age, ssu_age),
            solar_array_operating_temperature,
            solar_array_surviving_temperature,
            dummy_temperature,
            number_of_panels,
            panel_capacity,
            solar_array_operational_status,
            ssu_voltage_rating,
            ssu_threshold,
            ssu_wiring,
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
        # "t": "/system/clock/t",
        # "solar_irradiance": "/system/sun/solar_irradiance",
        # "external_temperature": "/system/surface/temperature",

        # # Power Generation - Solar Array
        # "solar_array_capacity": "/system/solar_array/generative_capacity",
        # "solar_array_power_output": "/system/solar_array/generate_power",

    }

    data = extract_data_from_saver(saver, _map)

    # # Surface Parameters 
    # fig, axs = plt.subplots(nrows=2)
    # axs[0].plot(data["t"], data["solar_irradiance"])
    # axs[0].set(ylabel="Irradiance", title="Temperature")

    # axs[1].plot(data["t"], data["external_temperature"])
    # axs[1].set(ylabel="Temperature")

    # # Solar Array
    # fig, axs = plt.subplots(nrows=2)
    # axs[0].plot(data["t"], data["solar_array_capacity"])
    # axs[0].set(ylabel="Capacity", title="Solar Arrays")
    # axs[1].plot(data["t"], data["solar_array_power_output"])
    # axs[1].set(ylabel="Power")

    # plt.show()
    # print("~~ovn!")