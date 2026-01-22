"""Model of the exterior environment

Author:
    Rashi Jain

Date:
    09.21.2023

"""

__all__ = ["SolarIrradiance"]

import numpy as np
from numbers import Number
from datetime import datetime, timedelta

from cdcm import *
from cdcm_utils import *
from cdcm_utils.solar_irradiation import get_insolation_ephemeris

# Plot Libraries 
import matplotlib.pyplot as plt

class SolarIrradiance(DataSystem):
    """Exterior environment depending on the location etc.."""
   
    def __init__(self, 
                 name: str,
                 clock: System, 
                 start_time: datetime, 
                 timesteps: Number,
                 *,
                 planet: str="moon", 
                 lat: Number=0.0, 
                 long: Number=0.0, 
                 **kwargs) -> None:
        self.planet = planet
        self.lat = lat
        self.long = long
        self.start_time = start_time
        self.dt = timedelta(**{clock.dt.units: clock.dt.value})
        self.timesteps = timesteps
        self.end_time = self.start_time + (self.timesteps - 1) * self.dt

        irradiation_data = get_insolation_ephemeris(
            start_time=self.start_time.isoformat(),
            end_time=self.end_time.isoformat(),
            step_size=str(int(clock.dt.value)) + clock.dt.units,
            phi=self.lat,
            lamda=self.long,
            alpha=0.0,
            beta=0.0
        )
        super().__init__(data=np.array(irradiation_data["Q"]),
                    name=name,
                    description="solar irradiance data for all timesteps",
                    columns="solar_irradiance",
                    column_units="W/m^2",
                    column_description="solar irradiance at selected location",
                    **kwargs)
        self.forward()


# Simulation parameters

time_steps = 500
start_time = datetime(2025, 1, 1)

if __name__ == "__main__":

    with System(name="system") as system:

        clock = make_clock(dt=1.0, units="hours")
        sun = SolarIrradiance("sun", clock, start_time, time_steps)

    file_name = __file__.split("/")[-1][:-3]

    system.forward()
    print(system)

    print(">.. Pyvis is making the HTML file.")

    tcs_graph = make_pyvis_graph(system)
    try:
        tcs_graph.show(file_name + ".html", notebook=False)
    except:
        tcs_graph.show(file_name + ".html")
    print(">... done")

    saver = SimulationSaver(
        file_name + ".h5",
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

        "irradiance": "/system/sun/solar_irradiance",
        }

    data = extract_data_from_saver(saver, _map)

    fig, axs = plt.subplots(nrows=1)

    axs.plot(data["t"], data["irradiance"])
    axs.set(ylabel="Irradiance (W/m^2)")

    plt.show()
    print("~~ovn!")