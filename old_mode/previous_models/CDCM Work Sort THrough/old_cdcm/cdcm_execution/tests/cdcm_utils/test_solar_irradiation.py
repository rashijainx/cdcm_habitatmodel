# ~ovn!
"""Test the solar irradiation model

Author:
    Sreehari Manikkan
    R Murali Krishnan
    
Date:
    01.30.2023
    05.08.2023
    
"""

from cdcm import *
from cdcm_utils.solar_irradiation import *

import numpy as np
import matplotlib.pyplot as plt


def make_exterior_environment(start_time, end_time, step_size, phi, lamda, alpha=0.0, beta=0.0):
    """Get an exterior environment model"""

    # Solar irradiation from Sreehari's model
    solar_irr = get_insolation_ephemeris(
        start_time=start_time,
        end_time=end_time,
        step_size=step_size,
        phi=phi,
        lamda=lamda,
        alpha=alpha,
        beta=beta,
    )

    # Instantiate a datasystem for exterior environment
    ext_env = DataSystem(
        name="ext_env",
        data=solar_irr['Q'].to_numpy(),
        columns=["Q"],
        column_units=["W/m^2"],
        column_descriptions=["Solar irradiation"]
    )
    ext_env.forward()
    ext_env.transition()
    return ext_env


start_time = "2022-01-10%2000:00"
end_times = ["2022-03-10%2000:00", "2023-01-10%2000:00"]
step_size = "1h"
phis = [0.7, 45.6, 88.5]
lamdas = [0.5, 88.5, -88.5]

with System(name="sys") as sys:

    clock = make_clock(dt=1.0, units="hr")

    ext_env = make_exterior_environment(start_time, end_times[0], step_size, phis[0], lamdas[0])

print(ext_env)