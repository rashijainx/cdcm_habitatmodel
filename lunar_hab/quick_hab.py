from database.all_database import battery_factory
from utils.factory import create_component

if __name__ == "__main__":

    rover_battery = create_component(
        "Rover Main Battery Pack",
        battery_factory,
        (10, 5, 0)
    )
