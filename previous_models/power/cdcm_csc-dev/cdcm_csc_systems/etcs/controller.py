"""Model of a controller in ETCS

Author: 
    Rashi Jain
    R Murali Krishnan

Date: 
    9/21/2023
    10/04/2023

"""

__all__ = ["make_controller"]


from cdcm import *
from cdcm_csc import *


def make_controller(
    clock: System,
    actuator_age_rate: NumOrVar,
    actuator_eccentric_amplitude: NumOrVar,
    external_dust_rate: NumOrVar,
    external_meteorite_impact: NumOrVar=None,
    **kwargs) -> System:

    with System(name="controller") as controller:

        # External Inputs
        power = make_component(name="power", nominal_health=1)

        optical_sensor = make_component(name="optical_sensor", nominal_health=1.0, Ed=10.0)

        # SOFTWARE (also affected by Power and Sensor)
        # Algorithm -> Continous (Erratic) / Non-continous (Algorithm Update)
        human_updates_algorithm = make_component(name="human_updates_algorithm", 
                                                 nominal_health=1.0)

        eccentric_behavior_algorithm = make_component(name="eccentric_behavior_algorithm",
                                                      dt=clock.dt,
                                                      health_damage_rate=actuator_eccentric_amplitude)

        # HARDWARE (age) - also affected by power
        # Replace when functionality if below a threshold
        hardware = make_component(name="hardware",
                                  dt=clock.dt,
                                  aging_rate=actuator_age_rate,
                                  Ed=10.0)

        # A maintainable component
        dust = make_maintainable_component(name="dust",
                                           dt=clock.dt,
                                           health_damage_rate=external_dust_rate,
                                           health_state_func=linear_function(),
                                           tools_to_repair=(("de_duster", 1),),
                                           consumables_to_repair=(("self_seal_barrier", 1),),
                                           tools_to_replace=(("end_effector_grasp_hard", 1),),
                                           consumables_to_replace=(("actuator_dust_lru", 1),
                                                                   ("self_seal_barrier", 2),))

        # A component of the actuator that can be affected by `meteorite` impact
        # actuator_meteorite = make_component(
        #     name="meteorite",
        #     clock=clock,
        #     health_damage_rate=external_meteorite_impact,
        #     health_state_func=linear_function(),
        # )

        agent_mishandling = make_component(name="agent_mishandling", nominal_health=1.0)

        # MOTION HARDWARE (bolts and bearing)
        actuator_bolts = make_component(name="bolts", nominal_health=1)

        actuator_bearing = make_component(name="bearing", nominal_health=1.0, Ed=10.0)

        actuator_functionality_inputs = (
            power,
            optical_sensor,
            human_updates_algorithm,
            eccentric_behavior_algorithm,
            hardware,
            dust,
            agent_mishandling,
            actuator_bolts,
            actuator_bearing,
        )

        actuator_functionality = make_functionality(*actuator_functionality_inputs)

    return controller



