#!/usr/bin/env python
# coding: utf-8

# In[12]:


from cdcm import *


# # State
# 
# State is a ```Variable``` whose value changes with time. Change in discrete
# time step is considered here. Two versions of value are stored for a State.
# The value of state at current time step is ```State.value``` and the value
# at next time step is ```State.next_value```.

# ### Creating a state

# In[13]:


s = State(
    value=0.5,
    units="m",
    track=True,
    description="A standard state."
)
print(s)


# In[14]:


print(f"The present value of the state is: {s._value}")


# In[15]:


print(f"The next value of the state is: {s._next_value}")


# In[16]:


s._next_value = 1.5
print("Changing the next value.")
print(f"The next value of the state is: {s._next_value}")


# In[17]:


print("Swaping values.")
s.transition()
print(s)


# *transition* is a function which swaps the values of State.value and State.next_value. More on transition function will be discussed later.

# ### Another way of creating a State
# Syntax: **make_node**("S:name:value:unit")

# In[18]:


x = make_node("S:x:1:m")
print(x)

