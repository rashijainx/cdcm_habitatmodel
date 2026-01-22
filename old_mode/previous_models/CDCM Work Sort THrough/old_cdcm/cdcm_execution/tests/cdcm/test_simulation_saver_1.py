"""Test the SimulationSaver class on a simple system.

Author:
    Ilias Bilionis

Date:
    3/15/2022


TODO: Use context to make saving safe.

"""


from cdcm import *
import numpy as np


# Make a system

x = make_node("S:x:0.1:meters", description="The state of the system.")
r = make_node("P:r:1.2:meters/second", description="The rate of change.")
dt = make_node("P:dt:0.1:second", description="The timestep.")
sigma = make_node("P:sigma:0.01:meters",
    description="The standard deviation of measurement noise.")
y = make_node("V:y", value=0.5, units="meters", description="A sensor measurement.")

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

max_steps = 10000
saver = SimulationSaver("test.h5", sys, max_steps=max_steps)

# Run and save
for i in range(max_steps):
    sys.forward()
    saver.save()
    if i % 1000 == 0:
        print(f"x: {sys.x.value:1.3f} {sys.y.value:1.3f}")
    sys.transition()

# Here is how you can get all the data saved so far
xs = saver.file_handler["/sys/x"][:]
print(xs)
ys = saver.file_handler["/sys/y"][:]
print(xs)