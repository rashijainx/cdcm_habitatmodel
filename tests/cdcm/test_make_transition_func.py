"""Test the transition function.


Author:
    Ilias Bilionis

Date:
    4/12/2022

"""


from cdcm import *
import yaml


print("TEST 1")
print("*" * 80)

# We will make a simple system with one state first
x = make_node("S:x:1:m")
r = make_node("P:r:0.1:1/s")
dt = make_node("P:dt:0.2:s")

# This the fast way to make a transition function
@make_function(x)
def f(x=x, r=r, dt=dt):
    return x + r * dt

# Print the entire computational graph
print(x)
print(r)
print(dt)
print(f)

# Test the transition
print("State before:")
print(x)
print("Evaluating the next step.")
f.forward()
print("State before transitioning:")
print(x)
x.transition()
print("State after:")
print(x)


# Now let's test a transition function that updates two states at the
# same time
print("TEST 2")
print("*" * 80)
x1 = make_node("S:x1:1.0:m")
x2 = make_node("S:x2:2.0:m")
@make_function(x1, x2)
def g(x1=x1, x2=x2, r=r, dt=dt):
    return (
        x1 + r * dt,
        x2 + x1 * dt
    )

# Print the entire computational graph
print(x1)
print(x2)
print(r)
print(dt)
print(g)

# Test the transition
print("State before:")
print(x1)
print(x2)
print("Evaluating the next step.")
g.forward()
x1.transition()
x2.transition()
print("State after:")
print(x1)
print(x2)