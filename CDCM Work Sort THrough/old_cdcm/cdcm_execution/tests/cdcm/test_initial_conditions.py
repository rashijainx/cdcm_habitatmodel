"""Tests initial conditions.

Author:
    Ilias Bilionis

Date:
    6/16/2022

"""


from cdcm import *
import numpy as np



with System(name="exp_decay", description="A simple oscilator") as sys:
    clock = make_clock(0.01)

    x = State(name="x", value=0.0, units="m",
        description="The position of the oscillator")

    # Initial conditions
    mu = Parameter(name="mu", value=0.0, units="m",
        description="The mean")
    sigma = Parameter(name="sigma", value=1.0, units="m",
        description="The standard deviation")

    # This sets the initial conditions of the state
    @make_function(x)
    def init_x(mu=mu, sigma=sigma):
        """Initializes x."""
        print("*** CALLING INIT ***")
        return mu + sigma * np.random.randn()

    # This sets the transition of the state
    omega = Parameter(name="omega", value=-1.3, units="m/sec",
        description="Decay rate")

    @make_function(x)
    def f(x=x, omega=omega, dt=clock.dt):
        print("*** CALLING TRANSITION ***")
        return x - dt * omega * x

    # Can we do this as follows?
    # mu = Parameter()
    # sigma = Parameter()
    # clock = make_clock()
    # with State("x") as x:
    #     x[0] ~ N(mu, sigma)
    #     x[t+1] = x[t] + clock.dt * omega * x[t]


print(sys)

# Simulate a trajectory
for i in range(10):
    sys.forward()
    print(f"t = {sys.clock.t.value:1.2f}, "
          + f"x = {sys.x.value:1.2f}, ")
    sys.transition()
