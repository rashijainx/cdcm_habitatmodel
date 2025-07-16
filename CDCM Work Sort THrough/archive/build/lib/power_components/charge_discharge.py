from cdcm import *
from cdcm_abstractions import *

__all__ = ["make_charging_station"]

def make_charging_station(
    name: str,
    clock: System,
    aging_rate: float,
    operating_temperature: tuple,
    surviving_temperature: tuple,
    temperature: Variable,
    tolerance: Variable,
    charging_rate: Variable,
    # Can have a switch to turn on and off. It can be power switch or something. 
) -> System:

    with System(name=name) as charging_station:

        operating_temp_min = Variable(
            name="operating_temp_min",
            value=operating_temperature[0]
        )
        operating_temp_max = Variable(
            name="operating_temp_max",
            value=operating_temperature[1]
        )
        surviving_temp_min = Variable(
            name="surviving_temp_min",
            value=surviving_temperature[0]
        )
        surviving_temp_max = Variable(
            name="surviving_temp_max",
            value=surviving_temperature[1]
        )

        age_rate = Variable(
            name="age_rate",
            value=aging_rate
        )

        @make_function(age_rate)
        def calc_age_rate(
            temp=temperature,
            omin=operating_temp_min,
            omax=operating_temp_max,
            smin=surviving_temp_min,
            smax=surviving_temp_max,
            ar=aging_rate
        ):
            if temp < omin or temp > omax:
                x = 1.0
            elif temp < smin or temp > smax:
                x = ar*2.0
            else:
                x = ar
            return x

        hardware = make_component(
            name="hardware",
            health_damage_rate=age_rate,
            dt=clock.dt,
            Ed=1.0
        )

        charge_functionality = make_functionality(
            hardware,
            name="charge_battery"
       )

        charge_rate = Variable(
            name="charge_rate", 
            value=charging_rate
        )

        @make_function(charge_rate)
        def calc_charge_rate(
            cr=charging_rate, 
            tol = tolerance, 
            health = charge_functionality
        ):
            if health > tol: 
                return cr*health
            else: 
                return 0.0
        
    return charging_station