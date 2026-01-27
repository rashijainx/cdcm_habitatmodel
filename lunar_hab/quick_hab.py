from core.system import System
from core.factory import create_component

from database.all_database import battery_factory


with System(name="MoonBase") as mysim:
    rover_batt = create_component(
        "Rover Main Battery Pack",
        "rover_batt",
        battery_factory,
        (10, 5, 0)
    )
