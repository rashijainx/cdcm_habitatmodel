"""Sensor with a Battery

Author:
    Rashi Jain

Date:
    02.13.2024
"""

from cdcm import *
from cdcm_constructs import *
import numpy as np

from .battery import make_battery

__all__ = ["make_sensor_assembly"]


def make_sensor_assembly(
        name: str,
        clock: System,
        battery_age_rate: float,
        sensor_age_rate: float,
        sensor_power_threshold: float,
        sensor_drift_behavior: float,
        sensor_random_behavior: float,
) -> System:

    with System(name=name) as sensor_assembly:

        battery = make_battery("battery",
                               clock,
                               battery_age_rate,
                               )

        age_rate = Variable(
            name="age_rate",
            value=sensor_age_rate,
        )
        power_threshold = Variable(
            name="power_threshold",
            value=sensor_power_threshold,
        )
        drift_behavior = Variable(
            name="drift_behavior",
            value=sensor_drift_behavior,
        )
        random_behavior = Variable(
            name="random_behavior",
            value=sensor_random_behavior,
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
                x = hardware*(1.0 - drift_behavior)*(1.0 - random_behavior*np.random.randn())
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

    return sensor_assembly
