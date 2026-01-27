__all__ = [
    "Function",
    "Transition",
    "make_function",
]

# Standard Imports 
from typing import Any, Callable, Tuple, NewType, Dict
from collections.abc import Iterable

# Incode Imports
from .node import Node
from .variable import Variable, State
from .utils import get_default_args

NodeTuple = NewType("NodeSet", Tuple["Node"])


class Function(Node):
    """A class representing a Function node.

    A Function has parents and children that are Variables. A Function
    essentially represents a function that takes as inputs the values of
    its parents and sets the values of its children. This action is
    carried out by overloading the `forward()` method.

    In functions, the order of the parents and the children is
    important. So, instead of using sets for parents and children,
    we are using tuples. This also means, the the parents and children
    of a function have to be specified when the function is made and
    they are immutable.

    Keyword Arguments:
    func -- A callable object with inputs and outputs that match the
            number and type of the parents and children of this node,
            respectively. For example, if this node has two parents
            `p1` and `p2` and one child `c`, then the function should be
            like this:
            ```
            def func(p1_value, p2_value, ...):
                # do some computations
                return c1_value, c2_value, ...
            ```
    parents -- The parents of the function. Here order matters.
    children -- The children of the function. Order matters.

    For the rest of the keyword arguments see `Node`.
    """

    def __init__(
        self,
        *,
        func : Callable,
        parents : NodeTuple,
        children : NodeTuple,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self._func = func
        if not isinstance(parents, Iterable):
            parents = (parents,)
        if not isinstance(children, Iterable):
            children = (children,)
        self.add_parents(parents)
        self.add_children(children)
        self._child_attr_to_update = "value"

    @property
    def func(self) -> Callable:
        """Get the function that this Function represents."""
        return self._func

    def to_dict(self) -> Dict[str, Any]:
        """Turn the object to a dictionary of dictionaries."""
        res = super().to_dict()
        dres = res[self.name]
        dres["func"] = self.func
        return res

    def _eval_func(self) -> Any:
        """Evaluates the function and returns the result."""
        try:
            return self.func(*(obj.value for obj in self.parents))
        except:
            raise TypeError(f"{self.name}._eval_func() is not defined properly. Please check your definition in ``{self.absname}``")

    def _update_children(self, result : Any, attr : str) -> None:
        """Writes `result` on `attr` of the children."""
        if not isinstance(result, tuple):
            result = (result, )
        for new_value, child in zip(result, self.children):
            setattr(child, attr, new_value)

    def forward(self) -> None:
        """Evaluates the next values of the children."""
        if self.parents_changed:
            super().forward()
            result = self._eval_func()
            self._update_children(result, self._child_attr_to_update)

    def __call__(self) -> None:
        """Runs self.forward()."""
        self.forward()


class Transition(Function):
    """A class representing a transition function.

    This is just like a function, but it assumes that all the outputs
    are of type `State`.
    So, instead of updating the current value of the output, it
    updates the next_value of the parents.

    **Do not include parents that are not of type `State`!!!**
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._child_attr_to_update = "_next_value"


def make_function(*args : Tuple[str, Variable]) -> Callable[[Callable], Function]:
    """Automate the creation of a function.

    The inputs to this decorator are the children states that will
    be updated by the transition function.
    """
    def make_function_inner(func : Callable) -> Function:

        if isinstance(args[0], str):
            func_name = args[0]
            children = args[1:]
        else:
            func_name = func.__name__
            children = args
        
        signature = get_default_args(func)
        parents = signature.values()
        # Check if we need a Function or a Transition.
        # We need a transition when the same variable appears
        # both in the parents and in the children and that variable
        # is a state
        set_c = set(parents)
        set_p = set(children)
        common_vars = set_c & set_p
        if common_vars:
            common_vars_state = all(isinstance(n, State) for n in set_p.intersection(set_c))
            if common_vars_state:
                FunctionType = Transition
            else:
                raise TypeError(
                f"`Function` node -> {func_name}(...) , have common `Variable` nodes as parents and children." + \
                " This behavior is only allowed for `State` nodes. Please check your definition."
                )
        else:
            FunctionType = Function
        return FunctionType(
            name=func_name,
            children=children,
            parents=parents,
            description=func.__doc__,
            func=func
        )

    return make_function_inner
