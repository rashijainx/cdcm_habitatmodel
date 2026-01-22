"""Tests quantities using pytest.

Author:
    Rashi Jain

Date:
    3/11/2022
"""


import numpy as np
from cdcm import *


# Testing floating point value
q = Variable(
    value=43.658123,
    units="m",
    name="q1",
    track=True,
    description="Some description.")
print(q)

# Testing integer value
q = Variable(
    value=1,
    units="km",
    name="q2",
    track=False,
    description="description"
)
print(q)

# It tests Variable class with arrays
arr_float = np.array([1.12, 2.2332, 3.34, 4.5326, 5.67])
q = Variable(
    value=arr_float,
    units="m",
    name="q3",
    track=False,
    description="description"
)
print(q)
