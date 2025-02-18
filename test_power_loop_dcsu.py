import matplotlib.pyplot as plt
import datetime

from cdcm import *
from cdcm_utils import *
from cdcm_abstractions import *

from structure import *
from power_components import *
from command_and_control_components import *

starting_epoch = datetime.datetime(2025, 1, 19)
time_steps = 1500

if __name__ == "__main__":
    with System(name="system") as system:

        clock = make_clock(dt=1.0, units="hours")

        sun = SolarIrradiance("sun", clock, starting_epoch, time_steps)
        # albedo = Variable(name="albedo", value=0.11)

        # surface = get_surface(
        #     "surface",
        #     sun.solar_irradiance,
        #     albedo,
        # )

        dummy_temperature = Variable(name="dummy_temperature", value=20.0)

        # Input these variables from YAML file for Solar Array 
        solar_array_age = Variable(name="solar_array_age", value=0.01/(24*365))
        solar_array_operating_temperature = (-100, 100)
        solar_array_surviving_temperature = (-275, 275)
        number_of_panels = Variable(name="number_of_panels", value=1)
        panel_capacity = Variable(name="panel_capacity", value=10)
        solar_array_operational_status = Variable(name="operational_status", value=1) 

        # Input these variables from YAML file for SSU 
        ssu_age = Variable(name="ssu_age", value=0.01/(24*365))
        ssu_operating_temperature = (-100, 100)
        ssu_surviving_temperature = (-275, 275)
        ssu_voltage_rating = Variable(name="ssu_voltage_rating", value=160.0)
        ssu_threshold = (0.75, 50000)
        ssu_wiring = (0.01/(24*365), 0.75)

        solar_array = make_integrated_array(
            "solar",
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

        # DCSU elements 
        sensor_age = Variable(name="sensor_age", value=0.01/(24*365))
        sensor_tolerance = Variable(name="sensor_tolerance", value=0.25)
        sensor_age_parameters = (sensor_age, sensor_tolerance)
        drift_parameter = Parameter(name="drift_parameter", value=25)
        noise_parameter = Parameter(name="noise_parameter", value=0.5)
        sensor_parameters = (drift_parameter, noise_parameter)
        
        sensor = make_sensor(
            "sunlight_sensor", 
            clock,
            sun.solar_irradiance,
            sensor_age_parameters,
            sensor_parameters,
        )

        power_demands = Variable(name="power_demands", value = 100) # W

        dcsu_age = 0.0; dcsu_tolerance = 0.5
        dcsu_age_parameters = (dcsu_age, dcsu_tolerance)
        dcsu_minimum_solar_requriement = Parameter(name="dcsu_minimum_solar_requirement", value=250)
        dcsu_voltage_rating = Variable(name="dcsu_voltage_rating", value=160.0)
    
        number_of_batteries = Parameter(name="number_of_batteries", value=4)

        dcsu = make_dcsu(
            "dcsu",
            clock,
            dcsu_age_parameters,
            dcsu_minimum_solar_requriement,
            dcsu_voltage_rating,
            sensor,
            solar_array,
            power_demands,
            number_of_batteries,
        ) 

        battery_age = 0.01/(24*365); battery_tolerance = 0.25
        battery_age_parameters = (battery_age, battery_tolerance)
        battery_operating_temperature = (-100, 100)
        battery_survival_temperature = (-275, 275)
        maximum_capacity = 10000

        bcdu_age = 0.01/(24*365); bcdu_tolerance = 0.5
        bcdu_age_parameters = (bcdu_age, bcdu_tolerance)

        battery_assembly = make_integrated_assembly_battery(
            "battery_assembly",
            clock,
            number_of_batteries,
            battery_age_parameters,
            battery_operating_temperature,
            battery_survival_temperature,
            dummy_temperature,
            maximum_capacity,
            dcsu,
            bcdu_age_parameters,
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
        "solar_irradiance": "/system/sun/solar_irradiance",
        # "external_temperature": "/system/surface/temperature",

        # Power Generation - Solar Array
        "solar_array_capacity": "/system/solar/array/generative_capacity",
        "solar_array_power_output": "/system/solar/array/generate_power",

        # Sequential Shunt Unit - Solar Array 
        "ssu_health": "/system/solar/ssu/hardware/functionality",
        "ssu_voltage": "/system/solar/ssu/voltage",

        # Sensor
        "sensor_health": "/system/sunlight_sensor/hardware/functionality",
        "sensor_functionality": "/system/sunlight_sensor/sense_sunlight",
        "sensor_measure": "/system/sunlight_sensor/measured_input",
        "sensor_error": "/system/sunlight_sensor/error",

        # DCSU 
        "dcsu_mode": "/system/dcsu/operational_mode",
        "dcsu_power_in": "/system/dcsu/battery_power_in",
        "dcsu_power_demand": "/system/dcsu/battery_power_demand",

        # Individual Battery
        "battery_charge": "/system/battery_assembly/3/battery/remaining_charge",
        "battery_functionality": "/system/battery_assembly/3/battery/provide_power",
    }

    data = extract_data_from_saver(saver, _map)

    # Surface Parameters 
    fig, axs = plt.subplots(nrows=2)
    axs[0].plot(data["t"], data["solar_irradiance"])
    axs[0].set(ylabel="Irradiance", title="Temperature")

    # axs[1].plot(data["t"], data["external_temperature"])
    # axs[1].set(ylabel="Temperature")

    # Solar Array
    fig, axs = plt.subplots(nrows=2)
    axs[0].plot(data["t"], data["solar_array_capacity"])
    axs[0].set(ylabel="Capacity", title="Solar Arrays")
    axs[1].plot(data["t"], data["solar_array_power_output"])
    axs[1].set(ylabel="Power")

    # Sequential Shunt Unit 
    fig, axs = plt.subplots(nrows=2)
    axs[0].plot(data["t"], data["ssu_health"])
    axs[0].set(ylabel="Health", title="SSU")

    axs[1].plot(data["t"], data["ssu_voltage"])
    axs[1].set(ylabel="Voltage")

    # Sensor 
    fig, axs = plt.subplots(nrows=3)
    axs[0].plot(data["t"], data["sensor_health"])
    axs[0].set(ylabel="Irradiance", title="Sensor")

    axs[1].plot(data["t"], data["sensor_functionality"])
    axs[1].set(ylabel="Voltage")

    axs[2].plot(data["t"], data["sensor_measure"])
    axs[2].plot(data["t"], data["solar_irradiance"])
    axs[2].set(ylabel="Measure")

    # DCSU
    fig, axs = plt.subplots(nrows=3)
    axs[0].plot(data["t"], data["dcsu_mode"])
    axs[0].set(ylabel="OM", title="DCSU")

    axs[1].plot(data["t"], data["dcsu_power_in"])
    axs[1].set(ylabel="Battery In")

    axs[2].plot(data["t"], data["dcsu_power_demand"])
    axs[2].set(ylabel="Battery In")


    # Battery
    fig, axs = plt.subplots(nrows=2)
    axs[0].plot(data["t"], data["battery_charge"])
    axs[0].set(ylabel="Charge", title="Battery")

    axs[1].plot(data["t"], data["battery_functionality"])
    axs[1].set(ylabel="Power Output")

    plt.show()
    print("~~ovn!")