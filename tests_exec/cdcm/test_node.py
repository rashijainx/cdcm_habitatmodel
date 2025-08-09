"""Testing the Node class.

Author:
    Ilias Bilionis

Date:
    4/12/2022

"""


from cdcm import *
import yaml


n1 = Node(
    name="n1"
)
n2 = Node(
    name="n2"
)

print(n1)
print(n2)

n1.add_child(n2)
print(n1)
print(n2)


n3 = Node(
    name="n3"
)

n3.add_parent(n1)

n4 = Node(
    name="n4"
)

n3.add_parent(n4)


print(n1)
print(n2)
print(n3)
print(n4)

# Test adding multiple children
n5 = Node(
    name="n5"
)
n6 = Node(
    name="n6"
)
n7 = Node(
    name="n7"
)
n8 = Node(
    name="n8"
)

# First, adding just one
n4.add_children(n5)
print(n4)

# Add from a sequence
n4.add_children([n6, n7])
print(n4)

# Test adding multiple parents
n6.add_parents([n7, n8])
print(n6)


print("Before removing parent n1 from n3:")
print(n1)
print("After removing parent n1 from n3:")
n1.remove_child(n3)
print(n1)
print(n3)
n3.remove_parent(n4)
n6.remove_parent(n4)
print(n3)
print(n4)

