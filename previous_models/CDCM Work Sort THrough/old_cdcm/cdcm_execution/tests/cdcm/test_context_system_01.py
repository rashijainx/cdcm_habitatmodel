"""Demonstrates the various equivalent ways in which we can define a
new system.

Author:
    Ilias Bilionis

Date:
    5/22/2022

"""


from cdcm import *
import numpy as np

# FIRST WAY - MANUAL
# Define all variables and compose the system mannually
x = State(name="x", value=0.1, units="meters")
r = Parameter(name="r", value=1.2, units="meters/second")
dt = Parameter(name="dt", value=0.1, units="second")
sigma = Parameter(name="sigma", value=0.1, units="meters")
y = Variable(name="y", value=0, units="meters")

@make_function(x)
def f(x=x, r=r, dt=dt):
    """The transition function."""
    return x + r * dt

@make_function(y)
def g(x=x, sigma=sigma):
    """An emission function."""
    return x + sigma * np.random.randn()

sys = System(
    name="sys",
    description="An isolated system",
    nodes=[x, r, dt, sigma, y]
    )

print(sys)

# SECOND WAY - INHERITANCE
class NewSystem(System):

    def define_internal_nodes(self, *args, **kwargs):
        """This function is run automatically when the system is
        initialized. The system keeps track of all the Nodes that are
        created inside here and adds them to its node list."""
        x = State(name="x", value=0.1, units="meters")
        r = Parameter(name="r", value=1.2, units="meters/second")
        dt = Parameter(name="dt", value=0.1, units="second")
        sigma = Parameter(name="sigma", value=0.1, units="meters")
        y = Variable(name="y", value=0, units="meters")

        @make_function(x)
        def f(x=x, r=r, dt=dt):
            """The transition function."""
            return x + r * dt

        @make_function(y)
        def g(x=x, sigma=sigma):
            """An emission function."""
            return x + sigma * np.random.randn()

sys = NewSystem(name="sys", description="An isolated system")

print(sys)

# THIRD WAY - INHERITANCE BUT WITH DECORATORS
@make_system
def sys():
    """An isolated system."""
    x = State(name="x", value=0.1, units="meters")
    r = Parameter(name="r", value=1.2, units="meters/second")
    dt = Parameter(name="dt", value=0.1, units="second")
    sigma = Parameter(name="sigma", value=0.1, units="meters")
    y = Variable(name="y", value=0, units="meters")

    @make_function(x)
    def f(x=x, r=r, dt=dt):
        """The transition function."""
        return x + r * dt

    @make_function(y)
    def g(x=x, sigma=sigma):
        """An emission function."""
        return x + sigma * np.random.randn()

# FOURTH WAY - CONTEXT MANAGER
with System(name="sys", description="An isolated system") as sys:
    x = State(name="x", value=0.1, units="meters")
    r = Parameter(name="r", value=1.2, units="meters/second")
    dt = Parameter(name="dt", value=0.1, units="second")
    sigma = Parameter(name="sigma", value=0.1, units="meters")
    y = Variable(name="y", value=0, units="meters")

    @make_function(x)
    def f(x=x, r=r, dt=dt):
        """The transition function."""
        return x + r * dt

    @make_function(y)
    def g(x=x, sigma=sigma):
        """An emission function."""
        return x + sigma * np.random.randn()

print(sys)

print("Run this forward:")
for i in range(10):
    sys.forward()
    print(f"x: {sys.x.value:1.3f} {sys.y.value:1.3f}")
    sys.transition()
