#!/usr/bin/env python
# coding: utf-8

# In[15]:


import numpy as np

from cdcm import *


# # Variable
# 
# Variable class is formed by directly inheriting Node
# class. Hence it has all the properties of Node class.
# Variable denotes a quantity with known unit. It has a description which explains
# what it is. It has a name also. Other attributes of variable are as follow:
# - ```value```: This is the value of the variable. It can be a scalar or array
#   of integer or float datatype. String value is also possible.
# - ```units```: The SI unit of the quantity which variable denotes.
# - ```track```: A boolean value which indicates whether to track or not the
#   variable during simulation.
# 
# <br>Variables with known unit and unchanging values are called as ```Parameters```.

# ### Creating a variable with floating point value

# In[16]:


q1 = Variable(
    value=53.5768,
    units="m",
    name="q1",
    track=True,
    description="mass of quantity 1")
print(q1)


# ### Creating a variable with integer value

# In[17]:


q2 = Variable(
    value=10,
    units="km",
    name="q2",
    track=False,
    description="rounded off distance"
)
print(q2)


# ### Creating a variable with an array of values

# In[18]:


arr_float = np.array([1.34, 2.7923, 5.11])
q3 = Variable(
    value=arr_float,
    units="m",
    name="q3",
    track=False,
    description="description"
)
print(q3)


# ### Another way of creating a variable
# Syntax is **make_node**("V:name:value:unit")

# In[19]:


q4 = make_node("V:q4:0.539:kg")
print(q4)

