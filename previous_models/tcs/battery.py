"""Model of a dummy sensor

Author:
    Rashi Jain

Date:
    1/31/2024 | Making Dummy Battery
"""
from cdcm import *
from cdcm_constructs import *

__all__ = ["make_battery"]


def make_battery(
    name: str,
    clock: System,
    battery_age_rate: float,
) -> System:

    with System(name=name) as battery:

        age_rate = Variable(name="age_rate", value=battery_age_rate)

        # HARDWARE
        hardware = make_component(
            name="hardware",
            health_damage_rate=age_rate,
            dt=clock.dt,
            Ed=1.0,
        )

        battery_functionality = make_functionality(
            hardware,
            name="generate_power"
        )

    return battery
