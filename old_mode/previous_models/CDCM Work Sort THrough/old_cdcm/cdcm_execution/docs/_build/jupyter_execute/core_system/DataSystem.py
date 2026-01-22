#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import numpy as np
import matplotlib.pyplot as plt

from cdcm import *


# # Data System
# 
# DataSystem class provides the functionality to read through a data sequence. We can access data from data system whenever required. A Data System object has following arguments:
# 
# ```data```: A data sequence<br>
# ```columns```: A sequence containing the names of each column. This will be string or sequence of string.<br>
# ```column_units```: SI unit if any of each column quantities. This will be string or sequence of string.<br>
# ```column_description```: Description for each column. This will be string or sequence of string.<br>
# ```column_track```: Track options for columns. This can be boolean or sequence of boolean values.<br>

# In[6]:


# Here are some random data
y = np.random.randn(10)

# And here is the system
random_sys = DataSystem(
    y,
    name="random_sys",
    description="A data system made from a pre-sampled random stream.",
    columns="omega",
    column_units="meters",
    column_desciptions="Some random quantity."
)

print(random_sys)


# In[7]:


for i in range(10):
    random_sys.forward()
    print(f"omega = {random_sys.omega.value:1.2f}")
    random_sys.transition()


# In[ ]:




