"""Abstractions required to specify transformations to Variables

Author:
    R Murali Krishnan
    
Date:
    09.22.2023
    
"""


from cdcm import *
from cdcm_csc import *


with System(name="sys") as sys:

    x = Variable(name="x", value=1.0)

    # default name is "<var_name>_scale"
    x_scaled = scale(x, 10.0)

print(sys)
sys.forward()

print(f"x.value: {x.value}, x_scaled.value: {x_scaled.value}")


