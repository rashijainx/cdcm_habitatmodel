import inspect
from typing import Any, Dict, Callable


def get_default_args(func : Callable) -> Dict[str, Any]:
    """Return a dictionary containing the default arguments of a
    function.

    I took this from here:
    https://stackoverflow.com/questions/12627118/get-a-function-arguments-default-value
    """
    signature = inspect.signature(func)
    return {
        k: v.default
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty
    }
