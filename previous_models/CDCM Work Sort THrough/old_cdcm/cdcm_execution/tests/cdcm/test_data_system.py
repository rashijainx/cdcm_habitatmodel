"""Test the DataSystem class.

Author:
    Ilias Bilionis

Date:
    3/14/2022

"""

from cdcm import *
import numpy as np


# Here are some random data
y = np.random.randn(10)

# And here is the system
rnd_sys = DataSystem(
    data=y,
    name="random_sys",
    description="A data system made from a pre-sampled random stream.",
    columns="omega",
    column_units="meters",
    column_descriptions="Some random quantity."
)

print(rnd_sys)

for i in range(10):
    rnd_sys.forward()
    print(f"omega = {rnd_sys.omega.value:1.2f}")
    rnd_sys.transition()
