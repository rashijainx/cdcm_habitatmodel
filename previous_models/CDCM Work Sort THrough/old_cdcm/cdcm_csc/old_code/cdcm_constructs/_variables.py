"""Core CDCM language abstractions for the models

Author:
    Ilias Bilionis
    R Murali Krishnan

Date:
    09/14/2022
    09.13.2023

"""


__all__  = ["HealthVariable", "BinaryHealthVariable", "ContinuousHealthVariable",
            "HealthState", "BinaryHealthState", "ContinuousHealthState",
            "Functionality"]


from cdcm import *
from typing import Union
from numbers import Number




class HealthVariable(Variable):
    """A class representing a health variable"""
    pass


class BinaryHealthVariable(HealthVariable):
    """A class representing a binary health state variable

    This is a `HealthState` variable which takes discrete binary values {0, 1}

    See `State` in the CDCM execution language for the keyword arguments.
    """

    pass


class ContinuousHealthVariable(HealthVariable):
    """A class representing a continuous health state variable"""
    pass


class HealthState(State):
    """A class representing a health state variable"""
    pass


class BinaryHealthState(HealthState):
    """A class representing a Binary health state variable

    This is a `HealthState` variable which takes binary values {0, 1}.
    """
    pass


class ContinuousHealthState(HealthState):
    """A class representing a continuous health state variable

    This is a `HealthState` variable which takes real number values.

    See `State` in the CDCM execution language for the keyword arguments
    """
    def __init__(self, *args, value, **kwargs) -> None:
        self.nominal_value = value
        super().__init__(*args, value=self.nominal_value, **kwargs)





class Functionality(Variable):
    """A class representing a functionality variable

    This is a `Variable` that represents the concept of a component functionality

    See `Variable` in the CDCM execution language for the keyword arguments.
    """

    def __init__(self, *args, nominal_value, **kwargs) -> None:
        self.nominal_value = nominal_value
        super().__init__(value=nominal_value, *args, **kwargs)


