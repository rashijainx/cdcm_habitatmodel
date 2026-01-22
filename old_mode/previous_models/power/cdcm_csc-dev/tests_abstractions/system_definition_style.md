# How should the definition of a system should look?

Discussion from Prof. Bilionis, Murali and Rashi

```python

from cdcm import *
from cdcm_csc import *
from csc_systems import *


with System(name="etcs") as etcs:
    
    clock = make_clock(dt=1.0)

    # Level 1 abstraction - Using the primitive abstractions 
    # of the execution language
    # Users should not deal with these abstractions directly
    dust = Parameter(name="dust", value=0.01/(24 * 365))

    aging_rate = Parameter(name="aging_rate", value=1./(24*365))

    with System(name="controller") as controller:

        # Level 2 Abstraction - Deriving variable types from the execution level abstractions
        # If users need access to some `Variable` types, we need to define them
        # at Level 2, so the user may use them for their models
        wire_aging_rate = HealthVariable(name="wire_aging_rate", value=0.0)
        @make_function(wire_aging_rate)
        def fn_wire_aging_rate(x1=hardware.health, x2=terminals.age):
            """Aging rat of the wires of the FDD"""
            return x1 * x2 

        # Level 3 abstractions - Component level behavior (atomic system element description)
        # Users use these abstractions to build atomic models of `System`s
        power_bus = make_component("power_bus",
                                   aging_rate=aging_rate,
                                   aging_func=linear_func_in_time,
                                   clock=clock)
        
        sensor = make_component("sensor", nominal_health=1)

        software = make_component("software", nominal_health=1)

        # Level 4 abstraction - Primitive system building blocks
        # Base subsystem models to define the CSC scenario
        with System(name="software") as software:

            code_check = make_component("code_check", nominal_health=1.0)

            # Extract the functionality of the components
            functionality = make_functionality("functionality", (power_bus, sensor, code_check))

        software = make_software(power, sensor)

        actuator = make_hardware(power, external_env, ...)


# A Level 5 abstraction provides a constructor to create the definition
# of a system with multiple components
controller = make_controller(power, external_env, ...)

etcs = make_etcs(...)

```

## Design of safety-controls in the framework

### Maintenance safety-controls

1. Regular maintenance

```python

def maintain(
    simulator: Simulator,
    component: Component, 
    period: Number, 
    end_time: Number,
    maintenance_coefficient: Number,
    ) -> Sequence[Events]
    """"""
    ...
    for t in range(now, final, period):
        def regular_maintenance_event():
            hv = component.health.value
            hv_nominal = component.nominal_health_value
            hv_new = min(hv * maintenance_coefficient, hv_nominal)
        simulator.add_event(t, regular_maintenance_event)
    return simulator
```

2. Condition-based maintenance

```python
def maintain(
    simulator: Simulator,
    variable: Variable, 
    period: Number, 
    end_time: Number,
    ) -> Sequence[Events]
    """"""
    ...
    for t start:final:period:
        
    return events
```


- Examples of creating systems with Level 4/5 abstraction
```python
with System(name="etcs") as etcs:
    
    # Parametets/Disruption timeseries

    controller = make_controller(
        clock,
        actuator_age_rate,
        actuator_eccentric_amplitude,
        external_dust_rate,
        external_meteorite_impact,
    )
    radiator_panel = make_radiator_panel(
        clock,
        panels_age_rate,
        external_dust_rate,
        external_meteorite_impact,
        controller,
    )
```

- Example of creating a Level 4/5 with Level 3 abstraction

```python
with System(name="controller") as controller:

    # External Inputs
    actuator_power = make_component(name="actuator_power", nominal_health=1)

    optical_sensor = make_component(name="optical_sensor", nominal_health=1.0)

    # SOFTWARE (also affected by Power and Sensor)
    # Algorithm -> Continous (Erratic) / Non-continous (Algorithm Update)
    human_updates_algorithm = make_component(
        name="human_updates_algorithm", nominal_health=1.0
    )
```

Conceptually talk about Level 3 abstraction