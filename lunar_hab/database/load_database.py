import yaml


def load_yaml(file_paths):

    library = {}

    if isinstance(file_paths, str):
        file_paths = [file_paths]

    for path in file_paths:
        try:
            with open(path, 'r') as f:
                data = yaml.safe_load(f)

                for category, item_list in data.items():
                    if not isinstance(item_list, list):
                        continue

                    for item in item_list:
                        if 'name' in item:
                            library[item['name']] = item

        except FileNotFoundError:
            print(" Warning: Could not find file path")
        except yaml.YAMLError as exc:
            print(f"Error parsing YAML: {exc}")

    return library
