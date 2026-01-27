__all__ = ["make_clock"]


from .factory import make_node
from .function import make_function
from .system import System


def make_clock(
    dt,
    t0=0.0,
    dt_name="dt",
    t_name="t",
    units="seconds",
    description="A system that counts time.",
    clock_name="clock"
):
    """Make a clock system."""
    with System(name=clock_name, description=description) as clock:
        pdt = make_node(f"P:{dt_name}:{dt}:{units}", description="The timestep.")
        t = make_node(f"S:{t_name}:{t0}:{units}", description="The time.")
        @make_function(t)
        def tick(t=t, dt=pdt):
            """Moves time forward by `dt`."""
            return t + dt
    return clock
