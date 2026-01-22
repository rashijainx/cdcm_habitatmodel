"""Test the Factor class.

Author:
    Ilias Bilionis

Date:
    4/14/2022

"""


from cdcm import *


# A simple function with one input and one output
node_in = make_node("V:node_in:0.5:m")
node_out = make_node("V:node_out", units="m")
f = Function(
    name="f",
    func=lambda x: x ** 2,
    parents=node_in,
    children=node_out
)
print(f)

print("Before we call forward:")
print(node_out)
print("After we call forward:")
f.forward()
print(node_out)
print(node_in)

# Here is the same Factor made using a decorator
print('*' * 80)
node_in = make_node("V:node_in:0.5:m")
node_out = make_node("V:node_out", units="m")
@make_function(node_out)
def f(x=node_in):
    return x ** 2
print(f)
print(node_in)
print(node_out)

print("Before we call forward:")
print(node_out)
print("After we call forward:")
f.forward()
print(node_out)

# Now let's test a function with multiple inputs and one output
print('*' * 80)
n1 = make_node("V:n1:0.6:m")
n2 = make_node("V:n2:1.0:s")
n3 = make_node("V:n3")
@make_function(n3)
def g(x=n1, y=n2):
    return x + y
print(g)
print("Before we call forward:")
print(n3)
print("After we call forward:")
g.forward()
print(n3)

# Same thing, but now with multiple outputs
print('*' * 80)
n1 = make_node("V:n1:0.6:m")
n2 = make_node("V:n2:2.0:s")
n3 = make_node("V:n3")
n4 = make_node("V:n4")
@make_function(n3, n4)
def g(x=n1, y=n2):
    return x + y, x * y
print(g)
print("Before we call forward:")
print(n3)
print(n4)
print("After we call forward:")
g.forward()
print(n3)
print(n4)


