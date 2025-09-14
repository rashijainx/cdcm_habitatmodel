"""Events that can manipulate base abstractions

Author:
    R Murali Krishnan
    
Date:
    09.21.2023
    
"""


from cdcm import *
from numbers import Number
from functools import partial, wraps


def event(func):
    """Decorator pattern for a generic event
    
    Arguments:
    ----------
    func    :   Callable
        Event function with specific behavior to be executed in
        a Simulator agenda.

    Return:
        event -> () :   Callable
            An event which executes as per the Simulator's agenda
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        return partial(func, *args, **kwargs)
    return wrapper


@event
def change_value(variable: Variable, new_value: Number):
    """An event that changes the value of a `cdcm.Variable`

    Arguments:
    ----------
    variable    :   cdcm.Variable 
        A cdcm.Variable object whose value will be changed by the event
    new_value   :   Number
        A number that represent the new value that the `variable` object should take
    """
    variable.value = new_value


@event
def switch_binary_value(variable):
    """Constructor of an event that changes the value of binary variable

    Arguments:
    ----------
    variable    :   cdcm.Variable 
        A variable that takes binary values

    """
    if variable.value == 0:
        new_value = 1
    elif variable.value == 1:
        new_value = 0
    else:
        raise TypeError(
            f"{variable.name} is a binary variable, it has a value {variable.value}"
        )
    return change_value(variable, new_value).__call__()
