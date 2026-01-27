from ast import literal_eval
from .node import Node
from .variable import Variable, State, Parameter
from .function import Function, Transition
from .component import Component, PhysicalComponent


CHAR_TO_NODE_TYPES = {
    "N": Node,
    "V": Variable,
    "S": State,
    "P": Parameter,
    "F": Function,
    "T": Transition
}


MAX_FIELDS_PER_TYPE = {
    "N": 2,
    "V": 4,
    "S": 4,
    "P": 4,
    "F": 2,
    "T": 2
}


def make_node(cmd, delimiter=":", **kwargs):
    """
    Makes a node from a string `cmd`

    The format of the string is:

        <type>:<name>:<value>:<units>

    The <type> is required and can be:
        N -- for Node
        V -- for Variable
        S -- for State
        P -- for Parameter
        F -- for Factor
        T -- for transition

    The <name> is requied and it should be a string.

    The <value> is optional and it is only valid for Variable, State,
    or Parameter.

    The <units> are optional and only valid for Variable, State, or
    Parameter. Note that you cannot specify the units without specifying
    a value.

    You can use keyword arguments to pass additional parameters to the
    class.

    Examples 1 (Node):
    ```
    n1 = make_node("N:n1")
    ```
    is equivalent to
    ```
    n1 = Node(name="n1")
    ```

    Example 2 (Variable):
    ```
    r1 = make_node("P:r1:0.5:s")
    ```
    is equivalent to:
    ```
    r1 = Parameter(
        name="r1",
        value=0.5,
        units=s
    )
    ```
    """
    fields = cmd.split(delimiter)
    if len(fields) < 2:
        raise ValueError(
            "At minimum you must specify a type and a name for making a node!"
        )
    type_char = fields[0]
    if type_char not in CHAR_TO_NODE_TYPES:
        raise ValueError(
            f"The supported node types are {CHAR_TO_NODE_TYPES.keys()}."
        )
    max_fields = MAX_FIELDS_PER_TYPE[type_char]
    if len(fields) > max_fields:
        raise ValueError(
            f"Type {type_char} supports up to {max_fields} fields."
        )
    NodeType = CHAR_TO_NODE_TYPES[type_char]
    name = fields[1]
    if len(fields) >= 3:
        value = literal_eval(fields[2])
        kwargs["value"] = value
    if len(fields) == 4:
        units = fields[3]
        kwargs["units"] = units
    return NodeType(name=name, **kwargs)

def create_component(
        name,
        iname,
        library,
        position,
):
    if name not in library:
        raise ValueError(f"Component '{name}' not found in the library")
    
    data = library[name]

    this_component = Component(name=name)
    
    if 'physical' in data:
        p_data = data['physical']
        this_component.physical = PhysicalComponent(
            name=iname,
            dimensions=p_data['dimensions'],
            shape=p_data['shape'],
            position=position,
            material=p_data['material']
        )

    return this_component