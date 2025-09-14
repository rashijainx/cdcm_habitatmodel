"""Test the clock.

Author:
    Ilias Bilionis

Date:
    3/15/2022
    4/16/2022
"""


from cdcm import *


clock = make_clock(0.1)

print(clock)

for i in range(10):
    clock.forward()
    print(f"time = {clock.t.value:1.2f}")
    clock.transition()
