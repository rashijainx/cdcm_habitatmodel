from cdcm import *
from cdcm_abstractions import *

from common_constructs import *

__all__ = [
    "make_bcdu",
    "make_rechargeable_battery",
    "make_integrated_battery", 
    "make_integrated_assembly_battery", 
]


def make_bcdu(
    name: str, 
    clock: System, 
    bcdu_age_parameters: tuple,
): 
    with System(name=name) as bcdu:

        charge_age = Variable(name="charge_age", value=bcdu_age_parameters[0])
        charge_tolerance = Variable(name="charge_tolerance", value=bcdu_age_parameters[1])

        bcdu_charge = make_component(
            name="bcdu_charge",
            health_damage_rate=charge_age,
            dt=clock.dt,
            Ed=1.0
        )
    
        discharge_age = Variable(name="discharge_age", value=bcdu_age_parameters[0])
        discharge_tolerance = Variable(name="discharge_tolerance", value=bcdu_age_parameters[1])
    
        bcdu_discharge = make_component(
            name="bcdu_discharge",
            health_damage_rate=discharge_age,
            dt=clock.dt,
            Ed=1.0
        )

        charge_functionality_inputs = (
            bcdu_charge,
            charge_tolerance,
        )

        def make_charge_functionality(
            hd=bcdu_charge,
            tol=charge_tolerance,
        ): 
            if hd > tol: 
                return 1
            else: 
                return 0
    
        charge_functionality = make_functionality(
            *charge_functionality_inputs,
            name="charge_battery",
            functionality_func=make_charge_functionality,
        )
        
        discharge_functionality_inputs = (
            bcdu_discharge,
            discharge_tolerance,
        )

        def make_discharge_functionality(
            hd=bcdu_discharge,
            tol=discharge_tolerance,
        ): 
            if hd > tol: 
                return 1
            else: 
                return 0
    
        disharge_functionality = make_functionality(
            *discharge_functionality_inputs,
            name="discharge_battery",
            functionality_func=make_charge_functionality,
        )

        return bcdu

def make_rechargeable_battery( 
    name: str,
    clock: System,
    temperature: Variable,
    age_parameters: tuple,
    operating_temperatures: tuple,
    surviving_temperatures: tuple,
    max_capacity: float, 
    bcdu: System,
    dcsu: System,
): 
    with System(name=name) as rechargeable_battery:

        aging = make_aging_component(
            "aging",
            clock,
            age_parameters,
            operating_temperatures,
            surviving_temperatures,
            temperature,
        )

        tolerance = Variable(
            name="tolerance",
            value=age_parameters[2]
        )

        battery_functionality_inputs = (
            aging.hardware,
            tolerance,
        )

        def make_battery_functionality(
            hd=aging.hardware,
            tol=tolerance,
        ): 
            if hd > tol: 
                return hd
            else: 
                return 0.0
        
        battery_functionality = make_functionality(
            *battery_functionality_inputs,
            name="store_power",
            functionality_func=make_battery_functionality
        ) 

        battery_capacity = State(
            name="battery_capacity",
            value=max_capacity
        ) 

        @make_function(battery_capacity)
        def calc_battery_capacity(
            bc = battery_capacity,
            bf = battery_functionality,
        ): 
            return bc*bf

        remaining_charge = State(
            name="remaining_charge",
            value=max_capacity,
            description="Remaining Battery Charge."
        )

        @make_function(remaining_charge)
        def calc_remaining_charge(
            maxc=battery_capacity,
            initial=remaining_charge,
            dmode=dcsu.operational_mode,
            power_io=dcsu.battery_power_change,
            bc = bcdu.charge_battery,
            bd = bcdu.discharge_battery,
        ):
            if dmode == 1 and bc > 0: 
                return  min(initial + power_io, maxc)
            elif dmode == -1 and bd > 0: 
                return max(0, initial - power_io)
            else:
                return initial
    
    return rechargeable_battery


def make_integrated_battery(
        name: str,
        clock: System,
        temperature: Variable,
        battery_age_parameters: tuple,
        battery_operating_temperature: tuple,
        battery_surviving_temperature: tuple,
        battery_max_capacity: float,
        bcdu_age_parameters: tuple,
        dcsu: System,
):
    with System(name=name) as integrated_battery:

        bcdu = make_bcdu(
            "bcdu", 
            clock,
            bcdu_age_parameters,
        )

        battery = make_rechargeable_battery(
            "battery",
            clock,
            temperature,
            battery_age_parameters,
            battery_operating_temperature,
            battery_surviving_temperature,
            battery_max_capacity,
            bcdu,
            dcsu,
        )
   
        return integrated_battery



def make_integrated_assembly_battery(
        name: str,
        clock: System,
        temperature: Variable,
        batteries: float,
        battery_age_parameters: tuple,
        battery_operating_temperature: tuple,
        battery_surviving_temperature: tuple,
        battery_max_capacity: float,
        bcdu_age_parameters: tuple,
        dcsu: System,
):
    with System(name=name) as integrated_assembly:

        number_of_batteries = Parameter(name="number_of_batteries", value=batteries)

        for i in range(1, number_of_batteries.value+1):
            integrated_battery = make_integrated_battery(
                str(i),
                clock,
                temperature,
                battery_age_parameters,
                battery_operating_temperature,
                battery_surviving_temperature,
                battery_max_capacity,
                bcdu_age_parameters,
                dcsu,
            )
   
        return integrated_assembly

