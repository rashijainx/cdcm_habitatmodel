from cdcm import *
from cdcm_abstractions import *

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
        bcdu_charge = make_component(
            name="bcdu_charge",
            health_damage_rate=charge_age,
            dt=clock.dt,
            Ed=1.0
        )
        discharge_age = Variable(name="discharge_age", value=bcdu_age_parameters[0])
        bcdu_discharge = make_component(
            name="bcdu_discharge",
            health_damage_rate=discharge_age,
            dt=clock.dt,
            Ed=1.0
        )
    
        tolerance = Variable(name="tolerance", value=bcdu_age_parameters[1])

        charge_functionality_inputs = (
            bcdu_charge,
            tolerance,
        )

        def make_charge_functionality(
            hd=bcdu_charge,
            tol=tolerance,
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
            tolerance,
        )

        def make_discharge_functionality(
            hd=bcdu_discharge,
            tol=tolerance,
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
    battery_age_parameters: tuple,
    operating_temperature: tuple,
    surviving_temperature: tuple,
    temperature: Variable,
    max_capacity: Variable, 
    bcdu: System,
    # power_demand: Variable,
    dcsu: System,
): 
    with System(name=name) as rechargeable_battery:

        remaining_charge = State(
            name="remaining_charge",
            value=max_capacity,
            description="Remaining Battery Charge."
        )

        battery_capacity = Variable(
            name="battery_capacity",
            value=max_capacity
        ) 
    
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

        aging_rate = Variable(
            name="aging_rate",
            value=battery_age_parameters[0]
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
            ar=aging_rate,
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

        bcdu_charge = bcdu.charge_battery
        bcdu_discharge = bcdu.discharge_battery

        dcsu_mode = dcsu.operational_mode
        power_demand = dcsu.battery_power_demand
        power_in = dcsu.battery_power_in

        @make_function(remaining_charge)
        def calc_remaining_charge(
            initial=remaining_charge,
            dmode=dcsu_mode,
            bc = bcdu_charge,
            bd = bcdu_discharge,
            pd=power_demand,
            pi=power_in,
            maxc=battery_capacity,
            # dt=clock.dt
        ):
            if dmode == -1 and bc > 0:
                return max(0, initial - pd)
            elif dmode == 1 and bd > 0:
                return max(0, min(initial + pi, maxc))
            else: 
                return initial
    
        tolerance = Variable(
            name="tolerance",
            value=battery_age_parameters[1]
        )
        battery_functionality_inputs = (
            hardware,
            tolerance,
            remaining_charge,
            power_demand,
        )

        def make_battery_functionality(
            hd=hardware,
            tol=tolerance,
            rc=remaining_charge,
            pd=power_demand,
        ):
            if hd > tol and rc > 0: 
                return pd
            else: 
                return 0
        
        battery_functionality = make_functionality(
            *battery_functionality_inputs,
            name="provide_power",
            functionality_func=make_battery_functionality
        )
        return rechargeable_battery

def make_integrated_battery(
        name: str,
        clock: System,
        battery_age_parameters: tuple,
        operating_temperature: tuple,
        surviving_temperature: tuple,
        temperature: Variable,
        battery_max_capacity: float,
        dcsu: System,
        bcdu_age_parameters: tuple,
        # bcdu_rates: tuple,
        # power_demand: Variable,
):
    with System(name=name) as integrated_battery:

        bcdu = make_bcdu(
            "bcdu", 
            clock,
            bcdu_age_parameters,
            # bcdu_rates,
            # dcsu_mode,
        )

        battery = make_rechargeable_battery(
            "battery",
            clock,
            battery_age_parameters,
            operating_temperature,
            surviving_temperature,
            temperature, 
            battery_max_capacity,
            bcdu,
            # power_demand,
            dcsu,
        )
   
        return integrated_battery

def make_integrated_assembly_battery(
        name: str,
        clock: System,
        number_of_batteries: Parameter,
        battery_age_parameters: tuple,
        operating_temperature: tuple,
        surviving_temperature: tuple,
        temperature: Variable,
        battery_max_capacity: float,
        dcsu: System,
        bcdu_age_parameters: tuple,
        # bcdu_rates: tuple,
        # power_demands: Variable,
):
    with System(name=name) as integrated_assembly:

        # power_demand = Variable(name="power_demand", value=power_demands.value/number_of_batteries.value)
        # dcsu_mode = dcsu.operational_mode
    
        for i in range(1, number_of_batteries.value+1):
            integrated_battery = make_integrated_battery(
                str(i),
                clock,
                battery_age_parameters,
                operating_temperature,
                surviving_temperature,
                temperature,
                battery_max_capacity,
                dcsu,
                bcdu_age_parameters,
                # bcdu_rates,
                # power_demand,
            )
   
        return integrated_assembly


# def make_battery(
#     name: str,
#     clock: System,
#     aging_rate: float,
#     operating_temperature: tuple,
#     surviving_temperature: tuple,
#     temperature: Variable,
#     initial_capacity: Variable,
#     tolerance: Variable,
#     discharge_rate: float,
#     voltage_rating: Variable,
#     operational_status: Variable,
# ) -> System:

#     with System(name=name) as battery:

#         remaining_charge = State(
#             name="remaining_charge",
#             value=initial_capacity,
#             units="m",
#             track=True,
#             description="Remaining Battery Charge."
#         )

#         operating_temp_min = Variable(
#             name="operating_temp_min",
#             value=operating_temperature[0]
#         )
#         operating_temp_max = Variable(
#             name="operating_temp_max",
#             value=operating_temperature[1]
#         )
#         surviving_temp_min = Variable(
#             name="surviving_temp_min",
#             value=surviving_temperature[0]
#         )
#         surviving_temp_max = Variable(
#             name="surviving_temp_max",
#             value=surviving_temperature[1]
#         )

#         age_rate = Variable(
#             name="age_rate",
#             value=aging_rate
#         )

#         @make_function(age_rate)
#         def calc_age_rate(
#             temp=temperature,
#             omin=operating_temp_min,
#             omax=operating_temp_max,
#             smin=surviving_temp_min,
#             smax=surviving_temp_max,
#             ar=aging_rate
#         ):
#             if temp < omin or temp > omax:
#                 x = 1.0
#             elif temp < smin or temp > smax:
#                 x = ar*2.0
#             else:
#                 x = ar
#             return x

#         hardware = make_component(
#             name="hardware",
#             health_damage_rate=age_rate,
#             dt=clock.dt,
#             Ed=1.0
#         )

#         @make_function(remaining_charge)
#         def calc_remaining_charge(
#             os=operational_status,
#             initial=remaining_charge,
#             dr = discharge_rate,
#             dt = clock.dt
#         ):
#             if os == 1:
#                 return max(initial - (dr*dt), 0)
#             else:
#                 return initial

#         battery_functionality_inputs = (
#             hardware,
#             remaining_charge
#         )
    
#         def make_battery_functionality(
#             rc=remaining_charge,
#             comp_health=hardware,
#         ):
#             return max(0, rc*comp_health)

        
#         battery_functionality = make_functionality(
#             *battery_functionality_inputs,
#             name="provide_power",
#             functionality_func=make_battery_functionality
#         )

#         voltage = Variable( 
#             name="voltage",
#             value=voltage_rating
#         )

#         @make_function(voltage) 
#         def calc_voltage(
#             os=operational_status,
#             health=hardware.functionality,
#             v=voltage_rating,
#             tol=tolerance,
#             power=battery_functionality
#         ):
#             if os==1 and health > tol and power > 0: 
#                 return v
#             else: 
#                 return 0
   
#     return battery   