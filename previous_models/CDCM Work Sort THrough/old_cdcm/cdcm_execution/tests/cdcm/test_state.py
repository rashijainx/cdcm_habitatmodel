"""Test the basic functionality of a state.

Author:
    Ilias Bilionis

Date:
    4/12/2022

"""


from cdcm import *
import yaml


s = State(
    value=0.5,
    units="m",
    track=True,
    description="A standard state."
)
print(s)

print(f"The next value of the state is: {s._next_value}")
s._next_value = 1.5
print("Changing the next value.")
print(f"The next value of the state is: {s._next_value}")
print("Swaping values.")
s.transition()
print(s)
