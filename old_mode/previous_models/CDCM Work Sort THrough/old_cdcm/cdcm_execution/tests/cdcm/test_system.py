"""Test the system class.

Author:
    Ilias Bilionis

Date:
    4/16/2022

"""


from cdcm import *
import matplotlib.pyplot as plt
import networkx as nx


r = make_node("P:r:0.1:1/s")
dt = make_node("P:dt:0.2:s")
x1 = make_node("S:x1:1.0:m")
x2 = make_node("S:x2:2.0:m")
@make_function(x1, x2)
def g(x1=x1, x2=x2, r=r, dt=dt):
    return (
        x1 + r * dt,
        x2 + x1 * dt
    )


sys = System(
    name="sys",
    nodes=[r, dt, x1, x2, g]
)

print(sys)
print(sys.states)

# You can access all the nodes like this:
print(sys.x1)
print(sys.x2)
print(sys.dt)
