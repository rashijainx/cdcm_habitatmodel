from cdcm import * 
from cdcm_utils import *
from cdcm_abstractions import *

__all__ = ["make_sleep"]

def make_sleep(
    name: str, 
) -> System: 
    with System(name=name) as sleep: 
        sleep_at_midnight = Variable(
            name="sleep_at_midnight",
            value = 1,
            description="Time to sleep at midnight."
        )

        sleep_in_bed = Variable(
            name="sleep_in_bed",
            value = 1,
            description="Rashi sleep in the bed."
        )

        wake_up = Variable(
            name="wake_up",
            description="Time to wake up."
        )

        @make_function(wake_up)
        def make_wake_up(
            midnight=sleep_at_midnight,
            bed=sleep_in_bed
        ) -> float:
            if midnight == 1 and bed == 1:
                return 0.5
            elif midnight == 1 and bed == 0: 
                return 1.0
            elif midnight == 0 and bed == 0:
                return 0.0
            else: 
                return 0.5
        
        return sleep 

if __name__ == "__main__":

    with System(name="rashi") as system:

        sleeo = make_sleep("sleep")


    print(system)

    print(">.. Pyvis is making the HTML file.")

    sys_graph = make_pyvis_graph(system)
    try:
        sys_graph.show("rashi.html", notebook=False)
    except:
        sys_graph.show("rashi.html")
    print(">... done")
