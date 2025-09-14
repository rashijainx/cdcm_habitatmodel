"""Test the meteorite damage mechanism

Author:
    R Murali Krishnan
    
Date:
    10.04.2023
    
"""


from cdcm import *
from cdcm_utils._io import extract_data_from_saver
from cdcm_csc_systems import *

from cdcm_utils import make_pyvis_graph
from test_systems import make_radiator_panel_assembly

import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt


start_time = datetime(2019, 10, 1)
time_steps = 7 * 30 * 24

# Initialize a grid for hab station
station_grid = Grid(7, 7)

with System(name="station") as station:

    clock = make_clock(dt=1.0, units="hours")

    dust_rate = State(name="dust_rate", value=1.0 / (24 * 365))
    @make_function(dust_rate)
    def fn_calculate_dust_rate(d=dust_rate, dt=clock.dt):
        return 1.0 / (24 * 365) + np.sqrt(dt) * 1e-5 * np.random.rand()

    sun = SolarIrradiance("sun", clock, start_time, time_steps)

    # radiator panel assembly
    radiator_assembly = make_radiator_panel_assembly(clock, 
                                                     sun.solar_irradiance,
                                                     1.0 / (24 * 365),  # actuator_age_rate
                                                     0.0,               # actuator_eccentric_amplitude
                                                     0.0,               # panels_age_rate
                                                     5.0 / (24 * 365))  # external_dust_rate
    # Place the radiator panel hardware
    radiator_panel_hardware = radiator_assembly.radiator_panel.hardware
    radiator_grid = [(i, j) for i in range(1, 3) for j in range(3, 6)]
    station_grid.place_system(radiator_panel_hardware, *radiator_grid)
    
    # Place the controller components
    controller = radiator_assembly.controller
    component_cluster = [controller.hardware, controller.bearing, controller.optical_sensor]
    for component in component_cluster:
        station_grid.place_system(component, (1,4))
    
    with System(name="assembly") as assembly:
        # ORU
        oru = make_component("oru", nominal_health=1.0, Ed=10.0)
        station_grid.place_system(oru, *[(5, i) for i in range(2, 5)])
        # Cold plate
        cold_plate = make_component("cold_plate", dt=clock.dt, health_damage_rate=dust_rate, Ed=10)
        station_grid.place_system(cold_plate, (4, 4))

        assembly_functionality = make_functionality(oru, cold_plate)

    station_functionality = make_functionality(assembly_functionality, radiator_assembly)
    

g = make_pyvis_graph(station)
try:
    g.show("test_meteorite_damage_mechanism.html")
except:
    g.show("test_meteorite_damage_mechanism.html", notebook=False)

print(str(station_grid))

saver = SimulationSaver("test_meteorite_damage_mechanism.h5", station, max_steps=time_steps, overwrite=True)

model = Simulator(station)

Eimpact = lambda Emin, Emax: Emin + (Emax - Emin) * np.random.rand()
sample_impact = lambda pos, t, Emax=0.1, Emin=0.0: Meteorite(pos, t, Eimpact(Emin, Emax))

# Adding meteorite events to `oru` every 10 hours
for t in range(0, time_steps, 10):
    impact = sample_impact((5,3), t)
    meteorite_damage_event = make_meteorite_event(station_grid, impact)
    if callable(meteorite_damage_event):
        model.add_event(t, meteorite_damage_event)

# Adding meteorite events to `cold_plate` every 25 hours
for t in range(0, time_steps, 25):
    impact = sample_impact((4,4), t)
    meteorite_damage_event = make_meteorite_event(station_grid, impact)
    if callable(meteorite_damage_event):
        model.add_event(t, meteorite_damage_event)

# Adding meteorite events to cluster of `radiator_panels` every 10 hours
for t in range(0, time_steps, 5):
    impact = sample_impact((1,4), t)
    meteorite_damage_event = make_meteorite_event(station_grid, impact)
    if callable(meteorite_damage_event):
        model.add_event(t, meteorite_damage_event)


for i in range(time_steps):
    model.forward()
    saver.save()
    model.transition()



_map = {
    "t": "/station/clock/t",
    "panels_hardware": "/station/etcs/radiator_panel/hardware/health",
    "controller_harware": "/station/etcs/controller/hardware/health",
    "controller_bearing": "/station/etcs/controller/bearing/health",
    "optical_sensor": "/station/etcs/controller/optical_sensor/health",
    "panel_functionality": "/station/etcs/radiator_panel/functionality",
    "cold_plate_health": "/station/assembly/cold_plate/health",
    "oru_health": "/station/assembly/oru/health",
    "assembly_functionality": "/station/assembly/functionality",
    "station_functionality": "/station/functionality"
}

data = extract_data_from_saver(saver, _map)

fig, axs = plt.subplots(nrows=2)
axs[0].plot(data['t'], data['cold_plate_health'])
axs[0].set(ylabel="Cold Plate Health")

axs[1].plot(data['t'], data['oru_health'])
axs[1].set(ylabel="ORU health")
fig.suptitle("ORU Cluster")
fig.tight_layout()

fig, axs = plt.subplots(nrows=2, ncols=2)
axs[0,0].plot(data['t'], data['panels_hardware'])
axs[0,0].set(ylabel="Radiator Panels (hardware)")

axs[1,0].plot(data['t'], data['controller_harware'])
axs[1,0].set(ylabel="Controller Hardware")

axs[0,1].plot(data['t'], data['controller_bearing'])
axs[0,1].set(ylabel="Controller Bearing")

axs[1,1].plot(data['t'], data['optical_sensor'])
axs[1,1].set(ylabel="Optical sensor")

fig.suptitle("Radiator Panel Cluster")
fig.tight_layout()


fig, axs = plt.subplots(nrows=3)
axs[0].plot(data['t'], data['panel_functionality'])
axs[0].set(ylabel="Radiator Panel Assembly\nfunctionality")

axs[1].plot(data['t'], data['assembly_functionality'])
axs[1].set(ylabel="ORU Assembly\nfunctionality")

axs[2].plot(data['t'], data['station_functionality'])
axs[2].set(ylabel="Station Functionality")

fig.suptitle("System Level Functionalities")
fig.tight_layout()

plt.show()

print("~~ovn!")

