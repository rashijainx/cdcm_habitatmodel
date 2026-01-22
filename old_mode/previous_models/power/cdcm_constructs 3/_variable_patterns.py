"""Standard behavior of Variable nodes

Author:
    R Murali Krishnan
    
Date:
    09.22.2023
    
"""


from cdcm import *
from numbers import Number
from typing import Callable
import operator as op
from functools import partial, reduce


def apply(variable: Variable, func: Callable, name: str=None) -> Variable:
    """Return a new Variable which applies a generic function to a Variable node
    
    Arguments:
    ----------
    name            :   str
        Name of the scaled variable
    variable        :   Variable
        Variable instance that needs the scaling
    func            :   Callable
        A callabe that creates the Function node
    """

    with System.get_context() as owner_system:

        transformed_variable_name = name if name is not None else variable.name + "_transformed"
        transformed_variable = Variable(name=transformed_variable_name, value=0.0)

        fn = Function(
            name=f"function_scale_{variable.name}",
            parents=(variable,),
            children=transformed_variable,
            func=func,
            description=f"Transformed variable {variable.name}"
        )
    return transformed_variable


def scale(variable: Variable, scaling_factor: Number, name: str=None):
    """Scaling transformation to a Variable node
    
    Arguments:
    ----------
    name            :   str
        Name of the sclaed variable
    variable        :   Variable
        Variable to which the scaling is applied
    scaling_factor  :   Callable
        Factor in which to scale the variable
    
    Return
    ------
        A Variable to which the scaling transformation is applied
    """
    scaling_func = lambda val, scale: val * scale
    new_name = name if name is not None else variable.name + "_scaled"
    return apply(name=new_name, variable=variable, func=partial(scaling_func, scale=scaling_factor))


def product(*args):
    """Product of all arguments"""
    return reduce(op.mul, args, 1)