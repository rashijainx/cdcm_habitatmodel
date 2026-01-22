"""Modified model of a controller in ETCS

Author: 
    Rashi Jain

Date: 
    9/21/2023

"""
from cdcm import *
from cdcm_csc import *


def make_controller(
    clock: System,
    actuator_age_rate: NumOrVar,
    actuator_eccentric_amplitude: NumOrVar,
    external_dust_rate: NumOrVar,
    external_meteorite_impact: NumOrVar,
    ) -> System:

    with System(name="controller") as controller:

        # External Inputs
        actuator_power = make_component(name="actuator_power", nominal_health=1)

        optical_sensor = make_component(name="optical_sensor", nominal_health=1.0)

        # SOFTWARE (also affected by Power and Sensor)
        # Algorithm -> Continous (Erratic) / Non-continous (Algorithm Update)
        human_updates_algorithm = make_component(
            name="human_updates_algorithm", nominal_health=1.0
        )

        eccentric_behavior_algorithm = make_component(
            name="eccentric_behavior_algorithm",
            dt=clock.dt,
            health_damage_rate=actuator_eccentric_amplitude,
            health_state_func=linear_function(),
        )

        # HARDWARE (age) - also affected by power
        # Replace when functionality if below a threshold
        actuator_hardware = make_component(
            name="actuator_hardware",
            dt=clock.dt,
            aging_rate=actuator_age_rate,
            aging_func=linear_function(),
        )

        # EXTERNAL HARDWARE (dust, meteorite impact)
        # actuator_dust = make_component(
        #     name="actuator_dust",
        #     clock=clock,
        #     health_damage_rate=external_dust_rate,
        #     health_state_func=linear_function,
        # )

        # A maintainable component
        actuator_dust = make_maintainable_component(
            name="actuator_dust",
            dt=clock.dt,
            health_damage_rate=external_dust_rate,
            health_state_func=linear_function(),
            tools_to_repair=(("de_duster", 1),),
            consumables_to_repair=(("self_seal_barrier", 1),),
            tools_to_replace=(("end_effector_grasp_hard", 1),),
            consumables_to_replace=(("actuator_dust_lru", 1),("self_seal_barrier", 2),)
        )

        actuator_meteorite = make_component(
            name="actuator_meteorite",
            dt=clock.dt,
            health_damage_rate=external_meteorite_impact,
            health_state_func=linear_function(),
        )

        agent_mishandling = make_component(name="agent_mishandling", nominal_health=1.0)

        # MOTION HARDWARE (bolts and bearing)
        actuator_bolts = make_component(name="actuator_bolts", nominal_health=1)

        actuator_bearing = make_component(name="actuator_bearing", nominal_health=1)

        actuator_functionality_inputs = (
            actuator_power,
            optical_sensor,
            human_updates_algorithm,
            eccentric_behavior_algorithm,
            actuator_hardware,
            actuator_dust,
            actuator_meteorite,
            agent_mishandling,
            actuator_bolts,
            actuator_bearing,
        )

        actuator_functionality = make_functionality(*actuator_functionality_inputs)

    return controller


if __name__ == "__main__":

    clock = make_clock(dt=1.0)

    actuator_age_rate = Parameter(
        name="actuator_age_rate", value=1.0 / (24 * 365)
    )  # Age 1%/ year
    actuator_erractic_amplitude = Parameter(
        name="actuator_erractic_amplitude", value=0.25
    )  # Amplitude 0.25
    external_dust_rate = Parameter(
        name="external_dust_rate", value=5.0 / (24 * 365)
    )  # Dust 1%/ year
    external_meteorite_impact = Parameter(
        name="external_meteorite_impact", value=0.5 / (24 * 365)
    )  # Meteorite Impact

    controller = make_controller(
        clock,
        actuator_age_rate,
        actuator_erractic_amplitude,
        external_dust_rate,
        external_meteorite_impact,
    )


    print(controller)
    controller.forward()

    g = make_pyvis_graph(controller)