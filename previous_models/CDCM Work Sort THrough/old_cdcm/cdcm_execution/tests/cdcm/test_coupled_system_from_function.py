"""Test a coupled system made out of functions.

Author:
    Ilias Bilionis

Date:
    3/15/2022
    4/16/2022
"""


from cdcm import *
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx


# ****************************
# System 0
# ****************************
clock = make_clock(0.1)

# ****************************
#       SYSTEM 1
# ****************************

x1 = make_node("S:x1:0.1:meters", description="State of sys1.")
r1 = make_node("P:r1:1.2:meters/second", description="Rate parameter for sys1.")
s1 = make_node(
    "P:s1:0.01:meters",
    description="Standard deviation of measurement noise"
)
y1 = make_node("V:y1", units="meters", description="Sensor measurement sys1.")

@make_function(x1)
def f1(x1=x1, r1=r1, dt=clock.dt):
    """Transition function for sys1."""
    return x1 + r1 * dt

@make_function(y1)
def g1(x1=x1, s1=s1):
    """Emission function for sys1."""
    return x1 + s1 * np.random.randn()

sys1 = System(
    name="sys1",
    nodes=[x1, r1, f1, s1, y1, g1]
)

# ****************************
#       SYSTEM 2
# ****************************

x2 = make_node("S:x2:0.3:meters")
r2 = make_node("P:r2:1.2:meters/second",)
c = make_node("P:c:0.1:1/second")
s2 = make_node(
    "P:s2:0.01:meters",
    description="Standard deviation of measurement noise"
)
y2 = make_node("V:y2", units="meters", description="Sensor measurement sys2.")


@make_function(x2)
def f2(x2=x2, x1=sys1.x1, r2=r2, c=c, dt=clock.dt):
    """Another simple system."""
    return x2 + r2 * dt + c * x1 * dt

@make_function(y2)
def g2(x2=x2, s2=s2):
    """Emission function for sys2."""
    return x2 + s2 * np.random.randn()

sys2 = System(
    name="sys2",
    nodes=[x2, r2, c, f2, s2, y2, g2]
)

# ****************************
#       COMBINED SYSTEM
# ****************************

sys = System(
    name="combined_system",
    nodes=[clock, sys1, sys2]
)

# ****************************
#       PRINT IN YAML
# ****************************

print(sys)

# ****************************
#       DRAW THE DAG
# ****************************
#g = sys.dag
#pos = nx.nx_agraph.graphviz_layout(g)
#nx.draw(g, with_labels=True, pos=pos)
#plt.show()

# ****************************
#       RUN FORWARD
# ****************************

for i in range(10):
    sys.forward()
    print(f"y1: {sys1.y1.value:1.2f}, y2: {sys2.y2.value:1.2f}")
    sys.transition()
