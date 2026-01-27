from core.system import System
from core.factory import create_component
from core.vis import make_pyvis_graph
from database.all_database import battery_factory


with System(name="MoonBase") as mysim:
    rover_batt = create_component(
        "Rover Main Battery Pack",
        "rover_batt",
        battery_factory,
        (10, 5, 0)
    )

pyvis_network = make_pyvis_graph(mysim)
print("Generating Graph")
pyvis_network.show("quick_hab.html", notebook=False)
print("Done! Open html in your browser")
