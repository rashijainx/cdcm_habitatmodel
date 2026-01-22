"""Model of the exterior environment

Author:
    Darin Lin
    R Murali Krishnan

Date:
    09.21.2023
    09.24.2023

"""


__all__ = ["SolarIrradiance"]


import numpy as np
from numbers import Number
from datetime import datetime, timedelta

from cdcm import *
from cdcm_utils.solar_irradiation import get_insolation_ephemeris


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
