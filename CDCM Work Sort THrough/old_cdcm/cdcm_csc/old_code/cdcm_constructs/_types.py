"""Types of arguments

Author:
    R Murali Krishnan
    
Date:
    10.04.2023
    
"""


from cdcm import Variable, Parameter, State
from numbers import Number
from typing import Union, Tuple, Sequence


NumOrVar = Union[Number, Variable, Parameter, State]
ToolSequence = Sequence[Tuple[str, Number]]
ConsumableSequence = Sequence[Tuple[str, Number]]