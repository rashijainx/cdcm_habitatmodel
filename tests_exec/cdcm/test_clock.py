"""Test the clock.

Author:
    Rashi Jain

Date:
    2023-10-15
"""


from cdcm import *


clock = make_clock(0.1)

print(clock)

for i in range(10):
    clock.forward()
    print(f"time = {clock.t.value:1.2f}")
    clock.transition()
