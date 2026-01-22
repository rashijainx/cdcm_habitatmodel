#~ovn!
"""Test the components of a power system

Author:
    R Murali Krishnan
    
Date:
    10.12.2023
    
"""


from cdcm import *
from cdcm_csc import make_pyvis_graph
from cdcm_csc._power import *

from functools import partial

replace = partial(replace, keep_old_owner=True)

max_steps = 700

num_gens, num_cons = 3, 3

with System(name="habitat") as hab:

    clock = make_clock(dt=1.0, units="hr")

    with System(name="power_system") as power_system:


        generators = []     
        for ngen in range(1, num_gens + 1):
            generator = make_power_generator(f"generator{ngen}", clock, 50.0)
            generators.append(generator)


        consumers = []
        for ncons in range(1, num_cons + 1):
            consumer = make_power_consumer(f"consumer{ncons}", clock, 75.0)
            consumers.append(consumer)
            
        with Distributor("distributor") as distributor:
            # distributor.connect(clock)

            for generator in generators:
                distributor.connect(generator)

            # Assumption: Consumers are connected in order of priority
            for consumer in consumers:
                distributor.connect(consumer)

        # Note: Unsupported behavior!!
        # distributor._compile()

hab.forward()
print("~ovn!")

print(power_system)

g = make_pyvis_graph(power_system)
try:
    g.show("test_power_systems.html")
except:
    g.show("test_power_systems.html", notebook=False)

