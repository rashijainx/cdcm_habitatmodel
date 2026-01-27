
__all__ = [
    "System",
    "make_system"
]


from typing import Any, Tuple, List
from functools import partial, cached_property
from contextlib import AbstractContextManager, nullcontext
import networkx as nx

from .node import Node, NodeSet
from .variable import State, Parameter
from .function import Function, Transition
from .utils import get_default_args


CHLD_INFERRED_MSG = "The children of a system are inferred - not specified."
PRNTS_INFERRED_MSG = "The parents of a system are inferred - not specified."


def replace_with_raise_error(
    Error : Exception,
    msg : str
):
    """This is used to replace a function with an error message."""
    def raise_error(*args : Any, **kwargs : Any):
        """Error message."""
        raise Error(msg)
    return raise_error

# fmt: off
replace_with_raise_value_error = partial(replace_with_raise_error, ValueError)

replace_chld_with_raise_value_error = replace_with_raise_value_error(CHLD_INFERRED_MSG)

replace_prnt_with_raise_value_error = replace_with_raise_value_error(PRNTS_INFERRED_MSG)
# fmt: on


class System(Node, AbstractContextManager):
    """A system represents a set of nodes.

    The nodes may be any class that inherits from Node.

    The system satisfies the following attributes:
        - The system owns its nodes.
        - The system exposes its nodes as attributes.
    """

    _contexts = []

    def __init__(
        self,
        nodes : NodeSet = set(),
        **kwargs
    ):
        super().__init__(**kwargs)
        if "children" in kwargs:
            raise ValueError(CHLD_INFERRED_MSG)
        if "parents" in kwargs:
            raise ValueError(PRNTS_INFERRED_MSG)
        self._nodes = list()

        self.add_child = replace_chld_with_raise_value_error
        self.add_children = replace_chld_with_raise_value_error
        self.remove_child = replace_chld_with_raise_value_error
        self.add_parent = replace_prnt_with_raise_value_error
        self.add_parents = replace_prnt_with_raise_value_error
        self.remove_parent = replace_prnt_with_raise_value_error
        self.add_nodes = partial(self._add_types, "node")

        self.add_nodes(nodes)

        with self if kwargs.get("add_internal_nodes", True) else nullcontext() as ctx:
            if ctx is not None:
                ctx.define_internal_nodes(**kwargs)

    def __enter__(self) -> "System":
        """Enter the context of the system to begin variable definitions."""
        System._contexts.append(self)
        return self

    def __exit__(self, typ, value, traceback):
        """Exit the context of the system."""
        System._contexts.pop()

    @staticmethod
    def in_context():
        """Returns true if we are currently in a context."""
        return bool(System._contexts)

    @staticmethod
    def get_context():
        """Get the current context."""
        return System._contexts[-1]

    @staticmethod
    def get_contexts():
        """Get the context stack."""
        return System._contexts

    def define_internal_nodes(self, **kwargs):
        """Define the internal nodes of the system.

        Overload this when defining a new system by inheriting from
        this class.
        """
        pass

    def add_node(self, obj, name=None):
        """Add a node."""
        if name is None:
            name = obj.name
        
        if name in self.__dict__.keys():
            raise ValueError(
f"While trying to add `{obj.name}` to `{self.name}`, I discovered that\n"
+ "there is another node owned by the system with the same name.\n"
+ "The original object is:\n"
+ str(self.__dict__[name]) + "\n"
+ "The object you are trying to add is:\n"
+ str(obj) + "\n"
+ "You have to rename one of the two."
            )
        self._nodes.append(obj)
        obj.owner = self
        self.__dict__[name] = obj

    @property
    def direct_nodes(self):
        """Get the nodes that are directly owned by this system."""
        return self._nodes

    @cached_property
    def nodes(self):
        """Get all the nodes that are inside this system.

        Note that this does not return subsystems, but the nodes of
        the subsystems. If you want to get the subystems, please use
        the subsystems property.
        """
        ns = set()
        for node in self.direct_nodes:
            if isinstance(node, System):
                ns.update(node.nodes)
            else:
                ns.add(node)
        return ns

    def to_dict(self):
        """Turn the object to a dictionary of dictionaries."""
        res = super().to_dict()
        dres = res[self.name]
        del dres["children"]
        del dres["parents"]
        dres["nodes"] = {}
        for n in self.direct_nodes:
            dres["nodes"].update(n.to_dict())
        return res

    def get_nodes_of_type(self, Type):
        """Get nodes of `Type`."""
        return set(
            filter(
                lambda n: isinstance(n, Type),
                self.nodes
            )
        )

    def remove_node(self, obj : Node,):
        """Removes a node from the system.

        Returns the name of and the object that was just removed.
        """
        self._nodes.remove(obj)
        del self.__dict__[obj.name]

    @cached_property
    def states(self) -> List[State]:
        return self.get_nodes_of_type(State)

    @cached_property
    def parameters(self) -> List[Parameter]:
        return self.get_nodes_of_type(Parameter)

    @cached_property
    def functions(self) -> List[Function]:
        return self.get_nodes_of_type(Function)

    @cached_property
    def transitions(self) -> List[Transition]:
        return self.get_nodes_of_type(Transition)

    @cached_property
    def subsystems(self) -> List['System']:
        """Return the subsystems of this system."""
        return set(
            filter(
                lambda n: isinstance(n, System),
                self._nodes
            )
        )

    def get_subsystems_of_type(self, Type) -> List['System']:
        """Return subsystems of certain `Type`"""
        return set(
            filter(
                lambda n: isinstance(n, Type),
                self.subsystems
            )
        )

    @cached_property
    def graph(self):
        """Turn the system to a directed graph.

        This is not necessarily acyclic.
        It is used for visualization purposes.

        For computational purposes, use dag.
        """
        g = nx.DiGraph()
        for n in self.nodes:
            g.add_node(n)
            for c in n.children:
                g.add_edge(n, c)
        return g

    @cached_property
    def dag(self):
        """Turns the system to a directed acyclic graph.

        Assumption:
            No more nodes have been added to the system since the last
            time that this was called.

            If you want to add more nodes after having added this, you
            have to make a new system object.
        """
        g = nx.DiGraph()
        for n in self.nodes:
            g.add_node(n)
            if isinstance(n, State):
                g.add_node(n.absname + "*")
            if isinstance(n, Transition):
                for c in n.children:
                    g.add_edge(n, c.absname + '*')
            else:
                for c in n.children:
                    g.add_edge(n, c)
        return g

    @cached_property
    def evaluation_order(self) -> Tuple[Node]:
        """This is the order in which the graph should be evaluted.

        Note that only Functions can be evaluated. So, this returns
        only functions.

        Assumption:
            No more nodes have been added to the system since the last
            time that this was called.

            If you want to add more nodes after having added this, you
            have to make a new system object.
        """
        return tuple(
            filter(
                lambda n: n in self.functions,
                nx.topological_sort(self.dag)
            )
        )

    def forward(self):
        """Moves all systems forward()."""
        for n in self.evaluation_order:
            n.forward()

    def transition(self):
        """Calls transition() on all nodes."""
        for t in self.states:
            t.transition()


def make_system(func):
    signature = get_default_args(func)
    parents = signature.values()
    with System(
        name=func.__name__,
        description=func.__doc__
    ) as sys:
        func(*parents)
    return sys
