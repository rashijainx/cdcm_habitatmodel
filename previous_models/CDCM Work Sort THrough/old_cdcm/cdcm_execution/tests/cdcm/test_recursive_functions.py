"""Test recursive functions in CDCM

Author:
    R Murali Krishnan
    
Date:
    06.02.2023
    
"""

from cdcm import *

# A simple recursive function with

n = make_node("V:n:10:")
fibn = make_node("V:fibn:0:")
@make_function(fibn)
def fn_fibn(n = n):

    def fib(n):
        if n <= 1:
            return n
        else:
            return n + fib(n - 1)
        
    return fib(n)

print(fn_fibn)
print(n)
print(fibn)

print('*' * 80)
print("Before we call forward")
print(fibn)
print()
print('*' * 80)
print("After we call forward")
fn_fibn.forward()
print(fibn)
print()
print('*' * 80)