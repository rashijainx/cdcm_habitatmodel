__all__ = [
    "Variable",
    "Parameter",
    "State",
]


import pint
from typing import Any, Dict
from numbers import Number
from copy import deepcopy

from .node import Node


ureg = pint.UnitRegistry()


class Variable(Node):
    """Defines a CDCM variable.

    The variable knows its units. It has a decscription that explains
    what it is. It has a name. And it has a value.

    Arguments
    ----------

        value       : int
            The value of the variable. Must be an `int`, a
            double or a numpy array of ints or floating point
            numbers. We also allow it to be a string.
            Initially, no value is specified. We are not
            going to check for the value of variables.
            But keep in mind that for saving them in files,
            the type has to be constant through out the life
            of the object.
        units       : str
            Must be a string or a pint object that describes
            an SI physical unit. This is optional as some
            variables may not have units.
        track       : bool
            A boolean. If True the variable will be tracked
            during simulations. If False it will not be
            tracked.

    See `Node` for the rest of the parameters.
    """

    def __init__(
        self,
        *,
        value : Any = None,
        units : str = "",
        track : bool = True,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.value = value
        self.units = units
        self.track = track

    @property
    def value(self) -> Any:
        """Get the value of the object."""
        return self._value

    @value.setter
    def value(self, new_value : Any):
        """Set the value of the object."""
        self._value = new_value
        self.tell_my_children_I_have_changed()

    @property
    def units(self) -> str:
        """Get the units of the object."""
        return self._units

    @units.setter
    def units(self, new_units : str) -> None:
        """Set the units."""
        ureg.check(new_units)
        self._units = new_units

    @property
    def track(self) -> bool:
        """Check if variable is being tracked during simulations or not."""
        return self._track

    @track.setter
    def track(self, new_track : bool) -> None:
        """Change the tracking flag."""
        self._track = new_track

    def to_dict(self) -> Dict[str, Any]:
        """Turn the object to a dictionary of dictionaries.

        TODO: make this more beautiful. Number does not work below.
        """
        res = super().to_dict()
        dres = res[self.name]
        if isinstance(self.value, Number):
            dres["value"] = self.value
        else:
            dres["value"] = str(self.value)
        dres["units"] = self.units
        dres["track"] = self.track
        return res

    def from_yaml(self, data : str) -> None:
        """TODO Write me."""
        raise NotImplementedError("This is not implemented yet.")


class Parameter(Variable):
    """A class representing a parameter of a system.

    See `Quantity` for the keyword arguments.
    """

    pass

class State(Variable):
    """A class representing a system state variable.

    This is a `Variable` that is changing in discrete steps.
    It stores two versions of its value.
    The current value is in `State.value`.
    The next value is in `State.next_value`.
    A call to `State._transition()` swaps `next_value` and `value`.

    See `Quantity` for the keyword arguments.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._next_value = deepcopy(self._value)

    def transition(self) -> None:
        """Writes `value` on `next_value`.

        Precondition:
        The `_next_value` has already been set.
        """
        self._next_value, self.value = self._value, self._next_value
        #self.tell_my_children_I_have_changed()
