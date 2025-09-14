"""Test the node factory.

Author:
    Ilias Bilionis

Date:
    4/14/2022


"""


from cdcm import *


# Make some nodes
n1 = make_node("N:n1")
n2 = make_node("N:n2", parents=n1)
print(n2)

# Make some variables
v1 = make_node("V:v1:0.5")
print(v1)
v2 = make_node("V:v2:1.5:m")
print(v2)
v3 = make_node("V:v3:1.5:m", description="Something in meters.")
print(v3)

# Make some parameters
p1 = make_node("P:p1:0.6:m")
print(p1)

p2 = make_node("P:p1:[0.5, 0.7]:m")
print(p2)
print(type(p2.value))