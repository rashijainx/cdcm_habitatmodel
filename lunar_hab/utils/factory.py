from core.component import(
    Component,
    PhysicalComponent
)


def create_component(
        name,
        library,
        position
):
    if name not in library:
        raise ValueError(f"Component '{name}' not found in the library")
    
    data = library[name]

    this_component = Component(name=name)
    if 'physical' in data:
        p_data = data['physical']
        this_component.physical = PhysicalComponent(
            dimensions=p_data['dimensions'],
            shape=p_data['shape'],
            position=position,
            material=p_data['material']
        )

    return this_component