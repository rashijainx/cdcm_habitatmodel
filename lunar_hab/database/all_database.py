import os
from .load_database import load_yaml

current_dir = os.path.dirname(os.path.abspath(__file__))
yaml_path = os.path.join(current_dir, 'batteries.yaml')

battery_factory = load_yaml(yaml_path)