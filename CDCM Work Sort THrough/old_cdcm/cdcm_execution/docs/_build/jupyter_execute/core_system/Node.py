#!/usr/bin/env python
# coding: utf-8

# In[18]:


from cdcm import Node


# # Node

# Node is the fundamental buidling block of the graph which represents a system
# in CDCM. All the components of the system will be represented as a Node object
# or object which inherits the Node. Node has attributes: <br>
# ``` name```: The name of the object.<br>
# ```description```: The description of the object.<br>
# ```parents```: The parents of the node. These are the nodes which affect the node.<br>
# ```children```: The children of the node. These are the nodes affected by the node.<br>
# ```owner```: The owner of the node. This can be the system of which the node is part of.<br>
# Following are some of the useful functionalities provided by the Node class:

# ### Creating a Node

# In[19]:


# A node n1 is created
n1 = Node(name="n1")
# A node n2 is created
n2 = Node(name="n2")
print(n1)
print(n2)

# Let us create more nodes
n3 = Node(name="n3")
n4 = Node(name="n4")
n5 = Node(name="n5")
n6 = Node(name="n6")
n7 = Node(name="n7")
n8 = Node(name="n8")


# ### Adding a node as a child of another node

# In[20]:


# n2 is added as a child of n1. This action implies n2 depends on n1.
n1.add_child(n2)
print(n1)
print(n2)


# ### Adding a node as a parent of another node

# In[21]:


n3.add_parent(n1)
n3.add_parent(n4)
print(n1)
print(n2)
print(n3)
print(n4)


# ### Adding multiple nodes as children of another node

# In[22]:


# First, adding just one
n4.add_children(n5)
print(n4)


# In[23]:


# Add from a sequence
n4.add_children([n6, n7])
print(n4)


# ### Adding multiple nodes as parents of another node

# In[24]:


n6.add_parents([n7, n8])
print(n6)


# ### Removing a parent from a child node (equivalently removing child node from the parent node)

# In[25]:


print("Before removing parent n1 from n3:")
print(n1)
print(n3)
print("After removing parent n1 from n3:")
n1.remove_child(n3) # same as n3.remove_parent(n1)
print(n1)
print(n3)


# In[26]:


n3.remove_parent(n4)
n6.remove_parent(n4)
print(n3)
print(n4)

