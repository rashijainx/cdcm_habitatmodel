import matplotlib.pyplot as plt
import datetime

import random

from cdcm import * 
from cdcm_utils import *
from cdcm_abstractions import * 

from structure import *
# from power_components import *

from solar_array import *
from sensor import *
from dcsu import *
from battery import * 
from voltage_regulator import *
from power_consumer import *
from switch import *

import numpy as np

starting_epoch = datetime.datetime(2025, 1, 19)
time_steps = 500

shift = 150


if __name__ == "__main__":
    with System(name="system") as system:

        clock = make_clock(dt=1.0, units="hours")

        sun = SolarIrradiance("sun", clock, starting_epoch, time_steps)

        lunar = get_surface(
            "lunar", 
            clock,
            sun.solar_irradiance,
            shift,
        )

        # INPUT PARAMETERS - FROM YAML FILE 
        solar_array_age = 2/(24*365); solar_array_radiation=1.1; solar_array_tolerance = 0.75
        solar_array_age_parameters = (solar_array_age, solar_array_radiation, solar_array_tolerance)
        solar_array_operating_temperatures = (-200, 200)
        solar_array_surviving_temperatures = (-200, 200)
        solar_array_power_multiplier=10

        solar_array_operational_status = 1

        ssu_age = 0.01/(24*365); ssu_radiation=0.1; ssu_tolerance = 0.5
        ssu_age_parameters = (ssu_age, ssu_radiation, ssu_tolerance)
        ssu_operating_temperatures = (-200, 220)
        ssu_surviving_temperatures = (-200, 200)
    
        ssu_voltage_rating = 160.0

        wiring_age = 0.01/(24*365); wiring_tolerance = 0.25
        wiring_aging_parameters = (wiring_age, wiring_tolerance)

        sensor_age = 0.01/(24*365); sensor_radiation = 1.1; sensor_tolerance = 0.75
        sensor_age_parameters = (sensor_age, sensor_radiation, sensor_tolerance)
        sensor_operating_temperatures = (-200, 220)
        sensor_surviving_temperatures = (-200, 200)
        sensor_drift = 25; sensor_noise = 0.5
        sensor_parameters = (sensor_drift, sensor_noise)
        all_sensor_parameters = (
            sensor_age,
            sensor_radiation,
            sensor_tolerance,
            sensor_operating_temperatures[0],
            sensor_operating_temperatures[1],
            sensor_surviving_temperatures[0],
            sensor_surviving_temperatures[1],
            sensor_drift,
            sensor_noise,
        )

        dcsu_age = 0.01/(24*365); dcsu_radiation = 1.1; dcsu_tolerance = 0.75
        dcsu_age_parameters = (dcsu_age, dcsu_radiation, dcsu_tolerance)
        dcsu_operating_temperatures = (-200, 200)
        dcsu_surviving_temperatures = (-200, 200)
        dcsu_power_need = 1000

        # Total Power Demand Downstream 
        power_demand = Variable(name="power_demand", value=2000.0)

        number_of_batteries = 4

        battery_age = 0.01/(24*365); battery_radiation = 0.0; battery_tolerance = 0.75
        battery_age_parameters = (battery_age, battery_radiation, battery_tolerance)
        battery_operating_temperatures = (-200, 200)
        battery_surviving_temperatures = (-200, 200)
        battery_max_capacity = 10000

        bcdu_age = 0.01/(24*365); bcdu_radiation = 0.0; bcdu_tolerance = 0.5
        bcdu_age_parameters = (bcdu_age, bcdu_tolerance)

        ddcu_age = 0.01/(24*365); ddcu_radiation = 0.0; ddcu_tolerance = 0.5
        ddcu_age_parameters = (ddcu_age, ddcu_radiation, ddcu_tolerance)
        ddcu_operating_temperatures = (-200, 200)
        ddcu_surviving_temperatures = (-200, 200)
        ddcu_voltage_rating = 126.0

        # To be calculated from input equipment to the DDCU 
        ddcu_power_demand_critical = 1000
        
        solar = make_integrated_array(
            "solar",
            clock,
            sun.solar_irradiance,
            lunar.temperature,
            solar_array_age_parameters,
            solar_array_operating_temperatures,
            solar_array_surviving_temperatures,
            solar_array_power_multiplier,
            solar_array_operational_status,
            ssu_age_parameters,
            ssu_operating_temperatures,
            ssu_surviving_temperatures,
            ssu_voltage_rating,
            wiring_aging_parameters,
        )

        dcsu = make_dcsu(
            "dcsu",
            clock,
            sun.solar_irradiance,
            lunar.temperature,
            dcsu_age_parameters,
            dcsu_operating_temperatures,
            dcsu_surviving_temperatures,
            number_of_batteries, 
            dcsu_power_need,
            power_demand,
            all_sensor_parameters,
            wiring_aging_parameters,
            solar.array
        )

        battery_assembly = make_integrated_assembly_battery(
            "battery_assembly",
            clock,
            lunar.temperature,
            number_of_batteries,
            battery_age_parameters,
            battery_operating_temperatures,
            battery_surviving_temperatures,
            battery_max_capacity,
            bcdu_age_parameters,
            dcsu,
        )

        ddcu = make_ddcu(
            "ddcu",
            clock,
            ddcu_age_parameters,
            ddcu_operating_temperatures,
            ddcu_surviving_temperatures,
            lunar.temperature,
            ddcu_voltage_rating,
            ddcu_power_demand_critical,
            wiring_aging_parameters,
            dcsu,
        )

        switch_age = 0.01/(24*365); switch_radiation = 0.0; switch_tolerance = 0.5
        switch_age_parameters = (switch_age, switch_radiation, switch_tolerance)

        fuse_age = 0.01/(24*365); fuse_radiation = 0.0; fuse_tolerance = 0.5
        fuse_age_parameters = (fuse_age, fuse_radiation, fuse_tolerance)

        heater_age = 0.01/(24*365); heater_radiation = 0.0; heater_tolerance = 0.5
        heater_aging_parameters = (heater_age, heater_radiation, heater_tolerance)

        heater_etcs_number = 4; heater_etcs_operational_status = 1; heater_etcs_power_consumption = 10; heater_etcs_voltage_rating = 120
        heater_power_consumer_spec = (heater_etcs_number, heater_etcs_operational_status, heater_etcs_power_consumption, heater_etcs_voltage_rating)
        heater_temperature_specs = (-200, 200, -200, 200)
        
        # Power Consumer (Heater)
        heater_etcs = make_multiple_integrated_power_consumer(
            "heater_etcs",
            "heat_equipment",
            clock, 
            lunar.temperature,
            heater_aging_parameters,
            heater_power_consumer_spec,
            heater_temperature_specs,
            switch_age_parameters,
            fuse_age_parameters,
            wiring_aging_parameters, 
            ddcu,
        )

        pump_age = 0.01/(24*365); pump_radiation = 0.0; pump_tolerance = 0.5
        pump_aging_parameters = (pump_age, pump_radiation, pump_tolerance)
        pump_etcs_number = 2; pump_etcs_operational_status = 1; pump_etcs_power_consumption = 10; pump_etcs_voltage_rating = 120
        pump_temperature_specs = (-200, 200, -200, 200)

        pump_power_consumer_spec = (pump_etcs_number, pump_etcs_operational_status, pump_etcs_power_consumption, pump_etcs_voltage_rating)
        pump_assembly = make_multiple_integrated_power_consumer(
            "pump_etcs",
            "pressurize_coolant",
            clock, 
            lunar.temperature,
            pump_aging_parameters,
            pump_power_consumer_spec,
            pump_temperature_specs,
            switch_age_parameters,
            fuse_age_parameters,
            wiring_aging_parameters,
            ddcu,
    
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
        "external_temperature": "/system/lunar/temperature",

        # Solar Array 
        "solar_array_hardware": "/system/solar/array/aging/hardware/functionality",
        "solar_array_gc": "/system/solar/array/generative_capacity",
        "solar_array_func": "/system/solar/array/generate_power",

        # Sequential Shunt Unit 
        "ssu_hardware": "/system/solar/ssu/aging/hardware/functionality",
        "ssu_functionality": "/system/solar/ssu/regulate_voltage",
        "ssu_voltage": "/system/solar/ssu/voltage",

        # # Sensor
        # "sensor_hardware": "/system/light_sensor/aging/hardware/functionality",
        # "sensor_functionality": "/system/light_sensor/sense_light",
        # "sensor_measure": "/system/light_sensor/measured_input"
    } 

    data = extract_data_from_saver(saver, _map)

    # # Surface Parameters 
    # fig, axs = plt.subplots(nrows=2)
    # axs[0].plot(data["t"], data["solar_irradiance"])
    # axs[0].set(ylabel="Irradiance",)

    # axs[1].plot(data["t"], data["external_temperature"])
    # axs[1].set(ylabel="Temperature")

    # # Solar Arrays 
    # fig, axs = plt.subplots(nrows=3) 
    # axs[0].plot(data["t"], data["solar_array_hardware"])
    # axs[0].set(ylabel="Hardware",)

    # axs[1].plot(data["t"], data["solar_array_gc"])
    # axs[1].set(ylabel="Capacity",)

    # axs[2].plot(data["t"], data["solar_array_func"])
    # axs[2].set(ylabel="Power Out",)

    # # Sequential Shunt Unit
    # fig, axs = plt.subplots(nrows=3) 
    # axs[0].plot(data["t"], data["ssu_hardware"])
    # axs[0].set(ylabel="Hardware",)

    # axs[1].plot(data["t"], data["ssu_functionality"])
    # axs[1].set(ylabel="Functionality",)

    # axs[2].plot(data["t"], data["ssu_voltage"])
    # axs[2].set(ylabel="Voltage",)

    # # Sensor
    # fig, axs = plt.subplots(nrows=3) 
    # axs[0].plot(data["t"], data["sensor_hardware"])
    # axs[0].set(ylabel="Hardware",)

    # axs[1].plot(data["t"], data["sensor_functionality"])
    # axs[1].set(ylabel="Functionality",)

    # axs[2].plot(data["t"], data["sensor_measure"])
    # axs[2].plot(data["t"], data["solar_irradiance"])
    # axs[2].set(ylabel="Light ",)

    # plt.show()
    # print("~~ovn!")