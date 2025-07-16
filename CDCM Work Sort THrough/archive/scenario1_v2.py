from cdcm import *
from cdcm_utils import *
from cdcm_abstractions import *


# Standard Python/Data Science libraries
import matplotlib.pyplot as plt
import numpy as np

import time # To time the simulation runs

# --- Simulation Parameters ---
simulation_total_time = 500.0 # hours
simulation_dt = 1.0           # hours (timestep)
num_steps = int(simulation_total_time / simulation_dt)

# --- Configuration ---
material_data_file = "material_properties.yaml"

# --- Output File Names ---
# Using generic names now as they contain multiple materials
pyvis_output_file = "habitat_aging_model_graph.html"
plot_output_file = "habitat_aging_comparison_results.png"

# --- Load Material Data ---
print(f"--- Loading Material Data from '{material_data_file}' ---")
try:
    material_data = parse_yaml(material_data_file)
    if 'materials' not in material_data or not isinstance(material_data['materials'], dict):
        raise ValueError(f"'materials' key not found or is not a dictionary in '{material_data_file}'.")
    if not material_data['materials']:
         raise ValueError(f"No materials defined under the 'materials' key in '{material_data_file}'.")

    materials_to_simulate = material_data['materials']
    print(f"Found {len(materials_to_simulate)} materials to simulate: {list(materials_to_simulate.keys())}")

except FileNotFoundError:
    print(f"ERROR: Material data file '{material_data_file}' not found.")
    exit()
except Exception as e:
    print(f"ERROR: Failed to load or parse material data file '{material_data_file}'.")
    print(f"Details: {e}")
    exit()

# --- Generate Pyvis Visualization (Once, for the structure) ---
# We generate this once using the first material's data just to show the graph structure
# The structure remains the same, only the parameter value changes.
print(f"\n--- Generating Pyvis graph for model structure ---")
try:
    first_material_name = list(materials_to_simulate.keys())[0]
    first_material_props = materials_to_simulate[first_material_name]
    first_aging_rate = first_material_props.get('aging_rate', 0.0) # Default if missing

    with System(name=f"habitat_aging_sim_STRUCTURE") as temp_system:
        clock = make_clock(dt=simulation_dt, units="hours")
        temp_aging_rate_param = make_node(f"P:material_aging_rate:{first_aging_rate}:1/hour")
        temp_outer_layer = make_component(
            name="outer_layer",
            dt=clock.dt,
            nominal_health=1.0, # Include nominal values
            nominal_age=1.0,
            aging_rate=temp_aging_rate_param,
            nominal_functionality=1.0,
            description=f"Outer structural layer (structure example)"
        )

    pyvis_graph = make_pyvis_graph(temp_system)
    pyvis_graph.save_graph(pyvis_output_file)
    print(f"Pyvis graph for model structure saved to '{os.path.abspath(pyvis_output_file)}'")
    del temp_system # Clean up temporary system

except Exception as e:
    print(f"Warning: Error generating Pyvis graph for structure: {e}")
    print("Ensure 'pyvis', 'seaborn', 'networkx' libraries are installed.")

# --- Data Storage for All Materials ---
all_results = {} # Dictionary to store results {material_name: {'times': [], 'age': [], 'func': []}}

# --- Main Simulation Loop for Each Material ---
print(f"\n--- Starting Simulations for All Materials ---")
total_sim_start_time = time.time()

for material_name, material_props in materials_to_simulate.items():
    sim_start_time = time.time()
    print(f"\n-- Simulating Material: '{material_name}' --")

    try:
        loaded_aging_rate = material_props['aging_rate']
        material_description = material_props.get('description', 'No description.')
        print(f"  Aging Rate: {loaded_aging_rate} (1/hour)")
    except KeyError:
        print(f"  WARNING: 'aging_rate' not defined for material '{material_name}'. Skipping.")
        continue # Skip this material if aging_rate is missing

    # --- Define System FOR THIS MATERIAL ---
    # We create a *new* system instance for each material to ensure isolation
    with System(name=f"habitat_aging_sim_{material_name}") as main_system:
        clock = make_clock(dt=simulation_dt, units="hours")
        material_aging_rate_param = make_node(
            f"P:material_aging_rate:{loaded_aging_rate}:1/hour",
            description=f"Aging rate for {material_name}."
        )
        outer_layer = make_component(
            name="outer_layer",
            dt=clock.dt,
            nominal_health=1.0, # Assuming functionality depends on age primarily
            nominal_age=1.0,
            aging_rate=material_aging_rate_param,
            nominal_functionality=1.0,
            description=f"Outer layer made of {material_name}."
        )

    # --- Set up Simulator FOR THIS MATERIAL ---
    simulator = Simulator(system=main_system)

    # --- Prepare Data Storage FOR THIS MATERIAL ---
    times = np.zeros(num_steps + 1)
    age_values = np.zeros(num_steps + 1)
    functionality_values = np.zeros(num_steps + 1)

    # Store initial state
    times[0] = main_system.clock.t.value
    age_values[0] = main_system.outer_layer.age.value
    functionality_values[0] = main_system.outer_layer.functionality.value

    # --- Run Simulation FOR THIS MATERIAL ---
    for i in range(num_steps):
        simulator.forward()
        simulator.transition()
        # Store results after transition
        times[i+1] = main_system.clock.t.value
        age_values[i+1] = main_system.outer_layer.age.value
        functionality_values[i+1] = main_system.outer_layer.functionality.value

    # --- Store Results for this Material ---
    all_results[material_name] = {
        'times': times,
        'age': age_values,
        'functionality': functionality_values,
        'aging_rate': loaded_aging_rate # Store for easy access in plotting
    }
    sim_end_time = time.time()
    print(f"  Simulation for '{material_name}' finished in {sim_end_time - sim_start_time:.2f} seconds.")
    # Optional: Clean up system and simulator if memory becomes an issue for many materials
    # del main_system, simulator

total_sim_end_time = time.time()
print(f"\n--- All simulations finished in {total_sim_end_time - total_sim_start_time:.2f} seconds ---")


# --- Plotting Comparison Results ---
print(f"\n--- Generating Comparison Plot ---")
fig, (ax_age, ax_func) = plt.subplots(2, 1, figsize=(12, 10), sharex=True) # Two subplots, shared x-axis

# Use color cycle for distinct lines
color_cycle = plt.cm.viridis(np.linspace(0, 1, len(all_results)))

for idx, (material_name, results) in enumerate(all_results.items()):
    rate = results['aging_rate']
    color = color_cycle[idx]

    # Plot Age Factor
    ax_age.plot(results['times'], results['age'],
                label=f"{material_name} (Rate: {rate:.2e})",
                color=color, marker='.', linestyle='-', markersize=3)

    # Plot Functionality
    ax_func.plot(results['times'], results['functionality'],
                 label=f"{material_name} Func.",
                 color=color, marker='x', linestyle='--', markersize=3)

# Formatting Age Plot
ax_age.set_ylabel("Age Factor (Unitless)")
ax_age.set_title("Habitat Outer Layer Aging Comparison")
ax_age.legend(loc='best', fontsize='small')
ax_age.grid(True)
ax_age.set_ylim(bottom=-0.05) # Start y-axis slightly below 0

# Formatting Functionality Plot
ax_func.set_ylabel("Functionality (Unitless)")
ax_func.set_xlabel(f"Time ({clock.t.units})") # Use clock units from last sim
ax_func.legend(loc='best', fontsize='small')
ax_func.grid(True)
ax_func.set_ylim(bottom=-0.05)

plt.tight_layout() # Adjust layout to prevent overlap

try:
    plt.savefig(plot_output_file)
    print(f"Comparison plot saved to '{os.path.abspath(plot_output_file)}'")
except Exception as e:
    print(f"Error saving comparison plot: {e}")

plt.show() # Display the plot

print("\n--- Script Complete ---")