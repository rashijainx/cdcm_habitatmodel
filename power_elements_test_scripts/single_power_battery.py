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

        battery_age_rate = Variable(name="battery_age_rate", value=0.01/(24*365))
        external_temperature = Variable(name="external_temperature", value=25.0)
        initial_charge = Variable(name="initial_charge", value=100.0)
        tolerance = Variable(name="tolerance", value=0.5)
        discharge_rate = Variable(name="discharge_rate", value=0.01)
        operational_status = Variable(name="operational_status", value=1)
        voltage_rating = Variable(name="voltage_rating", value=160.0)

        battery = make_battery(
            "battery",
            clock,
            battery_age_rate,
            (0, 45),
            (20, 30),
            initial_charge.value,
            tolerance,
            external_temperature,
            discharge_rate,
            voltage_rating, 
            operational_status,
        )

        dcsu_aging_rate = Variable(name="dcsu_aging_rate", value=0.01/(24*365))
        sun = SolarIrradiance("sun", clock, starting_epoch, time_steps)
        albedo = Variable(name="albedo", value=0.11)

        surface = get_surface(
            "surface", 
            sun.solar_irradiance,
            albedo,
        )

        dcsu = make_dcsu(
            "dcsu", 
            clock, 
            dcsu_aging_rate, 
            (0, 45), 
            (20, 30),
            surface.temperature,
        )

        ddcu_wiring_inputs =  (0.01/(24*365), 0.75, 125)      
        ddcu_age_rate = Variable(name="ddcu_age_rate", value=0.01/(24*365))
        ddcu_voltage_rating = Variable(name="ddcu_voltage_rating", value=160.0)
        ddcu_threshold = (0.75, 120)

        ddcu = make_ddcu(
            "ddcu",
            clock, 
            ddcu_age_rate, 
            (0, 45),
            (20, 30),
            ddcu_voltage_rating, 
            surface.temperature,
            ddcu_threshold,
            ddcu_wiring_inputs,
            battery
        )

        switch_aging_rate = 0.01/(24*365)
        fuse_aging_rate = 0.01/(24*365)
        power_consumer_spec = (1, 120)

        switch = make_integrated_switch(
            "switch", 
            clock, 
            switch_aging_rate,
            fuse_aging_rate, 
            ddcu.voltage,
            power_consumer_spec,
        )

        power_consumer_aging_rate = 0.01/(24*365)
        power_consumer = make_power_consumer(
            "power_consumer",
            clock,
            power_consumer_aging_rate,
            switch,
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

        # "temperature": "/system/temperature",

        # "solar_array_power_output": "/system/solar_array/generate_power", 
        
        # "ssu_functionality": "/system/ssu/regulate_voltage",
        # "ssu_voltage" : "/system/ssu/voltage",
        # "ssu_heat": "/system/ssu/heat",

    }

    data = extract_data_from_saver(saver, _map)

    fig, axs = plt.subplots(nrows=2)

    # axs[0].plot(data["t"], data["solar_irradiance"])
    # axs[0].set(ylabel="Irradiance", title="Temperature")

    # axs[1].plot(data["t"], data["temperature"])
    # axs[1].set(ylabel="Temperature")

    # fig, axs = plt.subplots(nrows=2)
    # axs[0].plot(data["t"], data["solar_array_power_output"])
    # axs[0].set(ylabel="Power Output", title="Solar Array Power Output")

    # fig, axs = plt.subplots(nrows=3)

    # axs[0].plot(data["t"], data["ssu_functionality"])
    # axs[0].set(ylabel="Function", title="Sequential Shunt Unit")

    # axs[1].plot(data["t"], data["ssu_voltage"])
    # axs[1].set(ylabel="Voltage")

    # axs[2].plot(data["t"], data["ssu_heat"])
    # axs[2].set(ylabel="Heat")
    # plt.show()
    # print("~~ovn!")