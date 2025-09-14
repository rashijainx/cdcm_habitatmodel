"""Common constructors used in the module

Author:
    Ilias Bilionis
    R Murali Krishnan
    
Date:
    09.18.2022
    10.04.2023

"""


__all__ = ["make_continuous_health_state_mechanism",
           "make_aging_mechanism",
           "make_health_mechanism",
           "make_functionality",
           "polynomial",
           "linear_function"]


from cdcm import *
from numbers import Number
from typing import Union, Callable, Optional
from functools import partial

from ._variables import *
from ._types import NumOrVar
from ._variable_patterns import product


def maybe_make_system(name_or_system: Union[str, System], clstype=System, **kwargs) -> System:
    """Returns either a new system with a given name or the system that is provided

    Arguments:
    ----------
    name_or_system  :   Union[str, System] 
        Handle of the System object
    clstype         : 
        System constructor type

    For the remaining kwargs refer to documentation of `cdcm.System`
    """

    if isinstance(name_or_system, str):
        # I am making a new system
        sys = clstype(name=name_or_system, **kwargs)
    elif isinstance(name_or_system, System):
        # I am just adding variables to an existing system
        sys = name_or_system
    else:
        raise ValueError(f"I do not know what to do with {type(name_or_system)}!")
    return sys


def polynomial(order: int, _clip: bool=True, lval: Number=0.0, uval: Number=1.0):
    """A polynominal function"""
    def f(state, dt, rate, *args, **kwargs):
        rate_term = [rate ** i for i in range(1, order + 1)]
        new_state = state - dt * sum(rate_term)
        return clip(new_state, lval, uval) if _clip else new_state
    return f


# State transition function which is linear to rate
linear_function = partial(polynomial, order=1)


def make_continuous_health_state_mechanism(dt: Parameter, 
                                           rate: NumOrVar, 
                                           func: Callable, 
                                           nominal_value: Number, 
                                           name: str, **kwargs) -> HealthState:
    """Make a continuous health state variable and create the state transition mechanism
    
    Arguments:
    ---------
    dt      :   Parameter
        Time step for integrating the health state
    rate    :   Union[Number, Varable]
        Rate at which the health state varies in time
    func    :   Callable
        State transition function (callable) with the following call signature
        ```
        def transition_function(state, dt, rate):
            ...
            new_state = f(state, dt, rate, ....)
            return new_state
        ```
    nominal_value   :   Number
        Nominal value of the health state
    name            :   str
        Type of health state

    Return
    ------
        Instantiated health state of the system
    """

    assert dt is not None and isinstance(dt, Parameter)
    assert isinstance(rate, (Number, Variable)), ("According to the arguments supplied, ",
                                                  "a continuous health state variable needs",
                                                  "to be creates. This requires a `rate` which",
                                                  "is either a Variable or a Number.",
                                                  f"argument of type -> {type(rate)} supplied.")

    if isinstance(rate, Number):
        if isinstance(nominal_value, float):
            rate = Parameter(name=name + "_rate", value=rate)
            statecls = ContinuousHealthState
        elif isinstance(nominal_value, int):
            raise TypeError("I can't support creation of binary health `State` variables yet..")
    else:
        statecls = ContinuousHealthState

    state = statecls(name=name, value=float(nominal_value))
    func = Transition(
        name=name + "_state_transition_func",
        parents=(state, dt, rate),
        children=state,
        func=func,
        description="Transition function of the continuous health state"
    )
    return state 


make_aging_mechanism = partial(make_continuous_health_state_mechanism, name="age")


def make_health_mechanism(dt: Parameter, 
                          health_damage_rate: Optional[NumOrVar], 
                          transition_func: Optional[Callable], 
                          nominal: Number, 
                          name: str="health", **kwargs) -> Union[HealthState, HealthVariable]:
    """Make a health transition mechanism
    Arguments:
    ---------
    dt      :   Parameter
        Time step for integrating the health state
    health_damage_rate    :   Optional[Union[Number, Varable]]
        Rate at which the health state varies in time. If `None`, a
        `HealthVariable` is created
    func    :   Optional[Callable]
        State transition function (callable) with the following call signature
        ```
        def transition_function(state, dt, rate):
            ...
            new_state = f(state, dt, rate, ....)
            return new_state
        ```
    nominal_value   :   Number
        Nominal value of the health state
    name            :   str
        Type of health state

    Return
    ------
        Instantiated health state of the system
    """

    assert isinstance(nominal, Number)
    if health_damage_rate is None:
        # This is a pure Variable, depending on type(nominal)
        cls = ContinuousHealthVariable if isinstance(nominal, float) else BinaryHealthVariable
        return cls(name=name, value=nominal, descriptipn="Health variable")
    else:
        assert callable(transition_func)
        return make_continuous_health_state_mechanism(dt, health_damage_rate, transition_func, nominal, name, **kwargs)
    # need a constructor for `BinaryHealthState` with a transition_function


def make_functionality(
        *args,
        name: str="functionality",
        functionality_func: Callable=product,
        nominal_functionality: Number=1.0,
        **kwargs) -> Functionality:
    """Create a functionality variable
    
    Arguments:
    ----------
    *args                   :   Sequence[Union[Variable, System]]
        A sequence of Variables or Systems with a variable `functionality`
    name                    :   str
        Name of the functionality variable to be created
    functionality_func      :   Callable
        A callable that can be executed to set the value of the functionality variable
    nominal_functionality   :    Number
        A number that specifies the nominal functionality value

    Return:
    -------
        Functionality variable whose value depends on the arguments passed to
        the function and the `functionality_func` procedure
    """

    functionality = Functionality(
        name=name,
        nominal_value=nominal_functionality,
        description="Functionality of the component"
    )

    if args:
        # Need to construct a functionality model
        assert callable(functionality_func)
        variables = []

        for arg in args:
            if isinstance(arg, System):
                assert hasattr(arg, "functionality"), \
                "[!] `System` instance does not have a functionality"
                variables.append(arg.functionality)
            elif isinstance(arg, Variable):
                variables.append(arg)
            else:
                raise TypeError("I need Variables to create a functionality")


        functionality_func = Function(
            name=name + "_function",
            parents=tuple(variables),
            children=functionality,
            func=functionality_func,
            description="A function that describes the functionality of the system"
    )
    return functionality