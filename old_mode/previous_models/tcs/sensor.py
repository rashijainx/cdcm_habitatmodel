"""Model of a dummy sensor

Author:
    Rashi Jain

Date:
    1/31/2024 | Making Dummy Sensor
"""
from cdcm import *
from cdcm_constructs import *

import numpy as np

__all__ = ["make_sensor"]


def make_sensor(
    name: str,
    clock: System,
    sensor_age_rate: float,
    sensor_power_threshold: float,
    sensor_drift_behavior: float,
    sensor_random_behavior: float,
    battery: System,
) -> System:

    with System(name=name) as sensor:

        age_rate = Variable(
            name="age_rate",
            value=sensor_age_rate,
        )
        power_threshold = Parameter(
            name="power_threshold",
            value=sensor_power_threshold
        )
        drift_behavior = State(
            name="drift_behavior",
            value=sensor_drift_behavior
        )
        random_behavior = Variable(
            name="random_behavior",
            value=sensor_random_behavior
        )

        # HARDWARE
        hardware = make_component(
            name="hardware",
            aging_rate=age_rate,
            dt=clock.dt,
            Ed=1.0,
        )

        def fn_functionality(
                hardware,
                power_threshold,
                drift_behavior,
                random_behavior,
                power
                ) -> float:
            if power < power_threshold:
                x = 0.0
            else:
                x = hardware*(1.0 - drift_behavior)*(1.0 - random_behavior*np.random.rand())
            return x

        sensor_functionality_inputs = (
            hardware,
            power_threshold,
            drift_behavior,
            random_behavior,
            battery.generate_power
        )

        sensor_functionality = make_functionality(
            *sensor_functionality_inputs,
            name="sense_source",
            functionality_func=fn_functionality
        )

    return sensor
