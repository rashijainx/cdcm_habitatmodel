""" Model of Pump in ETCS

Author:
    Noah Colasanti
    Rashi Jain 

Date: 
    10/6/2023
    10/10/2023 

"""

from cdcm import *
from cdcm_csc import *

def make_pump(
    clock: System,
    debris_intake_rate: NumOrVar,
    inlet_blockage_rate: NumOrVar,
    pump_age_rate: NumOrVar,
    cavitation_buildup_rate: NumOrVar,
    deadheading_rate: NumOrVar
    ) -> System:

    with System(name = 'pump') as pump:
        
        incorrect_maintenance = make_component(name = 'maintenance_procedure', nominal_health = 1)

        bolt_damage = make_component(name = 'bolt_failure', nominal_health = 1)

        pump_hardware =  make_component(
            name = 'pump_hardware',
            dt= clock.dt,
            health_damage_rate=pump_age_rate
        )

        jam = make_component(name = 'jam', nominal_health = 1)

        # metorite_impact = make_component(
        #         name = 'Metorite_impact',
        #         dt=clock.dt,
        #         health_damage_rate=external_meteorite_impact,
        #         health_state_func=linear_function()
        #     )
        
        pump_inputs = (
                incorrect_maintenance,
                bolt_damage,
                pump_hardware,
                jam
            )
        
        pump_functionality = make_functionality(*pump_inputs, name = 'pump_functionality')

        foreign_debris = make_component(
            name = 'foreign_debris',
            dt=clock.dt,
            health_damage_rate=debris_intake_rate
        )

        inlet_blockage = make_component(
            name = 'inlet_block', 
            dt= clock.dt,
            health_damage_rate=inlet_blockage_rate
        )

        cavitation = make_component(
            name = 'cavitation',
            dt= clock.dt,
            health_damage_rate=cavitation_buildup_rate
        )
        
        fluid_intake_inputs = (
            foreign_debris,
            inlet_blockage,
            cavitation
        )

        fluid_intake = make_functionality(*fluid_intake_inputs, name = 'fluid_intake')

        power_overload = make_component(name = 'power_overload', nominal_health=1)

        short_circuit = make_component(name = 'short_circuit', nominal_health=1)

        power_inputs = (
            power_overload,
            short_circuit
        )

        power_functionality = make_functionality(*power_inputs, name = 'power')

        dead_heading = make_component(
            name = 'deadheading',
            dt = clock.dt,
            health_damage_rate=deadheading_rate
        )

        fluid_output_inputs = (
            pump_functionality,
            fluid_intake,
            power_functionality,
            dead_heading
        )

        fluid_output_functionality = make_functionality(*fluid_output_inputs, name = 'fluid_output')

    return pump