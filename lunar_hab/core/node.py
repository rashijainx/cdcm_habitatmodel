__all__ = [
    "Node",
    "replace",
    "NodeSet"
]


import yaml
from collections.abc import Iterable
from typing import Any, Set, NewType, Dict
from functools import partialmethod


NodeSet = NewType("NodeSet", Set["Node"])


def get_context() -> 'System':
    """Return the current context, i.e., the system in which things are being created."""
    from .system import System
    return System.get_context()


def in_context() -> bool:
    """Returns true if we are currently in a context."""
    from .system import System
    return System.in_context()


class Node:
    """A node in a graph.

    Arguments
    ---------

    children    :
        The children of this node. The nodes that this node
        is affecting.
    parents     :
        The parents of the node. The nodes that are
        affecting this node.
    owner       :
        The owner of the node - if any. In our application
        this is a system
    name        : 
        The name of the object. The user must definitely
        provide a name.
    description :
        The description of the object. Optional.

    Extra keyword arguments are ignored.
    """

    _TYPE_DICTS = {
        "child": "children",
        "parent": "parents"
    }

    _REFLECTION = {
        "child": "parent",
        "parent": "child"
    }

    def __init__(
        self,
        *,
        name : str = "unamed_node",
        description : str = "",
        children : NodeSet = list(),
        parents : NodeSet = list(),
        owner : Any = None,
        **kwargs
    ) -> None:
        self.name = name
        self.description = description
        self.owner = owner
        self._children : NodeSet = list()
        self._parents : NodeSet = list()
        self._parents_changed = False
        self.add_children(children)
        self.add_parents(parents)
        if in_context():
            get_context().add_node(self)

    @property
    def children(self) -> NodeSet:
        """Get the children."""
        return self._children

    @property
    def parents(self) -> NodeSet:
        return self._parents

    @property
    def parents_changed(self) -> bool:
        return self._parents_changed

    @parents_changed.setter
    def parents_changed(self, value : bool):
        self._parents_changed = value

    def tell_my_children_I_have_changed(self) -> None:
        """If you run this, then the forward() of this node will be called during the next iteration."""
        for c in self.children:
            c.parents_changed = True

    def add_child(self, obj : "Node", reflexive : bool = True) -> None:
        self._children.append(obj)
        if reflexive:
            obj.add_parent(self, reflexive=False)

    def add_parent(self, obj : "Node", reflexive : bool = True) -> None:
        self._parents.append(obj)
        self.parents_changed = True
        if reflexive:
            obj.add_child(self, reflexive=False)

    def _add_types(
        self,
        type_of_nodes : str,
        objects : NodeSet
    ) -> None:
        """Adds may parents or children.

        See `add_parents()` and `add_children()` for usage.
        """
        if not isinstance(objects, Iterable):
            objects = (objects, )
        add_func = getattr(self, f"add_{type_of_nodes}")
        for item in objects:
            add_func(item)

    add_children = partialmethod(_add_types, "child")
    add_parents = partialmethod(_add_types, "parent")

    def remove_child(self, obj : "Node", reflexive : bool = True) -> None:
        self.children.remove(obj)
        if reflexive:
            obj.remove_parent(self, reflexive=False)

    def remove_parent(self, obj : "None", reflexive : bool = True) -> None:
        self.parents.remove(obj)
        if reflexive:
            obj.remove_child(self, reflexive=False)

    @property
    def owner(self) -> Any:
        """Get the owner of this object."""
        return self._owner

    @owner.setter
    def owner(self, new_owner : Any) -> None:
        """Set the owner of this object."""
        self._owner = new_owner

    @property
    def name(self) -> str:
        """Get the name of the object."""
        return self._name

    @name.setter
    def name(self, name : str) -> None:
        """Set the name
         of the object."""
        assert isinstance(name, str), (
            f"{name} is not a string. Names must be strings!"
        )
        self._name = name

    @property
    def absname(self) -> str:
        if self.owner is not None:
            return self.owner.absname + '/' + self.name
        return self.name

    @property
    def description(self) -> str:
        """Get the description of the object."""
        return self._description

    @description.setter
    def description(self, dsc : str) -> None:
        """Set the description of the object."""
        if dsc is None:
            dsc = ""
        dsc = str(dsc)
        self._description = dsc

    def __str__(self) -> str:
        """Return a string representation of the object."""
        return self.to_yaml()

    def to_dict(self) -> Dict:
        """Turn the object to a dictionary of dictionaries."""
        get_name = lambda x: x.name if x.owner is self.owner else x.absname
        parents_str = str(tuple(map(get_name, self.parents)))
        children_str = str(tuple(map(get_name, self.children)))
        return {
            self.name: {
                "description": self.description,
                "owner": str(self.owner.absname) if self.owner is not None else "",
                "parents": parents_str,
                "children": children_str
            }
        }

    def to_yaml(self) -> str:
        """Turn the object to yaml."""
        return yaml.dump(self.to_dict(), sort_keys=False)

    def from_yaml(self, data : str) -> None:
        """Set the parameters of the object from a dictionary."""
        raise NotImplementedError("This feature hasn't yet been implemented!")

    def forward(self) -> None:
        """This is provided for symmetry. To be overloaded by Factor."""
        self.parents_changed = False

    def transition(self) -> None:
        """This is provided for symmetry. To be overloaded by State."""
        pass


def replace(
    old_node : Node,
    new_node : Node,
    keep_old_owner : bool = False
) -> None:
    """Replace an old node with a new node.

    Keyword Arguments:
    keep_old_owner -- If True new_node.owner becomes old_node.owner.
    """
    for p in old_node.parents:
        i = p.children.index(old_node)
        p.children[i] = new_node
        new_node.add_parent(p, reflexive=False)
    old_node.parents.clear()
    for c in old_node.children:
        i = c.parents.index(old_node)
        c.parents[i] = new_node
        new_node.add_child(c, reflexive=False)
    old_node.children.clear()
    old_owner = old_node.owner
    if old_owner is not None:
        old_owner.remove_node(old_node)
        if keep_old_owner:
            new_owner = new_node.owner
            if new_owner is not None:
                new_owner.remove_node(new_node)
            old_owner.add_node(new_node)
