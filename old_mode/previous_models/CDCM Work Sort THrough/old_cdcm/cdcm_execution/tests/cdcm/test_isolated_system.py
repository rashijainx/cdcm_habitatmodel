"""Tests the functionality of the System class for a simple isolated system.

Author:
    Ilias Bilionis
    Murali Krishnan R

Date:
    3/14/2022

"""


from cdcm import *
import numpy as np



x = make_node("S:x:0.1:meters", description="The state of the system.")
r = make_node("P:r:1.2:meters/second", description="The rate of change.")
dt = make_node("P:dt:0.1:second", description="The timestep.")
sigma = make_node("P:sigma:0.1:meters",
    description="The standard deviation of measurement noise.")
y = make_node("V:y", units="meters", description="A sensor measurement.")

@make_function(x)
def f(x=x, r=r, dt=dt):
    """The transition function."""
    return x + r * dt

@make_function(y)
def g(x=x, sigma=sigma):
    return x + sigma * np.random.randn()

sys = System(
    name="sys",
    nodes=[x, r, dt, f, g, y],
    description="An isolated system."
)

print(sys)

print("Run this forward:")
for i in range(10):
    sys.forward()
    print(f"x: {sys.x.value:1.3f} {sys.y.value:1.3f}")
    sys.transition()
