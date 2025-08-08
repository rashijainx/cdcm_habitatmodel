"""Make a coupled system using with statemetns.

Author:
    Ilias Bilionis

Date:
    3/15/2022
    4/16/2022
    5/22/2022
"""


from cdcm import *
import numpy as np


with System(name="combined_system") as sys:
    # Make a clock
    clock = make_clock(0.1)

    # Make system 1
    with System(name="sys1") as sys1:
        x1 = State(name="x1", value=0.1, units="meters")
        r1 = Parameter(name="r1", value=1.2, units="meters/second",
            description="Rate parameter")

        @make_function(x1)
        def f1(x1=x1, r1=r1, dt=clock.dt):
            """Transition function for sys1."""
            return x1 + r1 * dt

        with System(name="sensor"):
            s1 = Parameter(name="s1", value=0.01, units="meters",
                description="Standard dev. measurement noise")
            y1 = Variable(name="y1", value=0.0, units="meters",
                description="Sensor output")
            @make_function(y1)
            def g1(x1=x1, s1=s1):
                return x1 + s1 * np.random.randn()

    with System(name="sys2") as sys2:
        x2 = State(name="x2", value=0.3, units="meters")
        r2 = Parameter(name="r2", value=1.2, units="meters")
        c = Parameter(name="c", value=0.1, units="1/second")

        @make_function(x2)
        def f2(x2=x2, x1=sys1.x1, r2=r2, c=c, dt=clock.dt):
            """Another simple system."""
            return x2 + r2 * dt + c * x1 * dt

        with System(name="sensor"):
            s2 = Parameter(name="s2", value=0.01, units="meters")
            y2 = Variable(name="y2", units="meters")
            @make_function(y2)
            def g2(x2=x2, s2=s2):
                return x2 + s2 * np.random.randn()

print(sys)

# ****************************
#       RUN FORWARD
# ****************************

for i in range(10):
    sys.forward()
    print(f"y1: {sys1.sensor.y1.value:1.2f}, y2: {sys2.sensor.y2.value:1.2f}")
    sys.transition()
