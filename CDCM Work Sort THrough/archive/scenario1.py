from cdcm import *
from cdcm_utils import *
from cdcm_abstractions import *


# Standard Python/Data Science libraries
import matplotlib.pyplot as plt
import numpy as np
import random


# --- Simulation Parameters ---
simulation_total_time = 131400 # hours
simulation_dt = 1.0           # hours (timestep)

# --- Meteorite Impact Parameters (for the separate variable) ---
impact_interval = 100.0 # hours
min_impact_value = 0.01
max_impact_value = 0.02

material_data_file = "material_properties.yaml"

target_material_name = "Cast_Regolith"
print(f"--- Loading Material Data from '{material_data_file}' ---")
try:
    material_data = parse_yaml(material_data_file)
    if 'materials' not in material_data or target_material_name not in material_data['materials']:
        raise KeyError(f"Material '{target_material_name}' not found in '{material_data_file}' under 'materials' key.")

    selected_material_props = material_data['materials'][target_material_name]
    loaded_aging_rate = selected_material_props['aging_rate']
    material_description = selected_material_props.get('description', 'No description.') # Optional description

    print(f"Successfully loaded properties for material: '{target_material_name}'")
    print(f"  Aging Rate: {loaded_aging_rate} (1/hour)")
    print(f"  Description: {material_description}")

except FileNotFoundError:
    print(f"ERROR: Material data file '{material_data_file}' not found.")
    print("Please create the YAML file in the same directory.")
    exit() # Stop script if data file is missing
except KeyError as e:
    print(f"ERROR: {e}")
    print("Please check the structure of your YAML file and the target_material_name.")
    exit() # Stop script if material is missing
except Exception as e:
    print(f"ERROR: Failed to load or parse material data file '{material_data_file}'.")
    print(f"Details: {e}")
    exit()

# material_choice_damage_rate = 0.0005 # unitless health points lost per hour
#                                       # (e.g., 0.001 means 10% degradation in 100h if linear)
#                                       # !! CHANGE THIS VALUE FOR DIFFERENT MATERIALS !!

# --- Output File Names ---
pyvis_output_file = "habitat_simulation_graph.html"
plot_output_file = "habitat_simulation_results.png"
impact_plot_file = "habitat_impact_variable_plot.png"

# --- Define the System using the 'with' context manager ---
print("--- Defining System ---")
with System(name="habitat_simulation") as main_system:

    # 1. Create the simulation clock
    clock = make_clock(dt=simulation_dt, units="hours")
    print(f"Clock created with dt={clock.dt.value} {clock.dt.units}")

    # 2. Define the material property (as a parameter)
    material_aging_rate_param = make_node(
        f"P:material_aging_rate:{loaded_aging_rate}:1/hour",
        description=f"Aging rate for material '{target_material_name}' ({material_description})."
    )
    print(f"Material aging parameter created: {material_aging_rate_param.name} = {material_aging_rate_param.value}")


    # 3. Create the Outer Structure Layer Component
    outer_layer = make_component(
        name="outer_layer",
        dt=clock.dt,
        nominal_health=1.0,
        health_damage_rate=material_aging_rate_param,
        nominal_functionality=1.0,
        description="The outer structural layer of the habitat."
    )
    print(f"Component '{outer_layer.name}' created.")

print("\n--- System Definition Complete ---")
print(main_system)

# --- Generate Pyvis Visualization ---
print(f"\n--- Generating Pyvis graph ---")
try:
    pyvis_graph = make_pyvis_graph(main_system)
    pyvis_graph.save_graph(pyvis_output_file)
    print(f"Pyvis graph saved")
    # Optional: Show the graph directly if in an interactive environment
    # pyvis_graph.show(pyvis_output_file, notebook=False) # Opens in browser
except Exception as e:
    print(f"Error generating Pyvis graph: {e}")
    print("Ensure 'pyvis' and 'seaborn' libraries are installed.")

# --- Set up the Simulator ---
print("\n--- Initializing Simulator ---")
simulator = Simulator(system=main_system)
print("Simulator created.")

# --- Prepare Data Storage for Plotting ---
num_steps = int(simulation_total_time / simulation_dt)
times = np.zeros(num_steps + 1)
health_values = np.zeros(num_steps + 1)
functionality_values = np.zeros(num_steps + 1)

# Store initial state (t=0)
times[0] = main_system.clock.t.value
health_values[0] = main_system.outer_layer.health.value
functionality_values[0] = main_system.outer_layer.functionality.value

# --- Run the Simulation ---
print(f"\n--- Starting Simulation: {num_steps} steps ---")

print(f"Time: {times[0]:>6.2f} hr | "
      f"Outer Layer Health: {health_values[0]:>6.4f} | "
      f"Functionality: {functionality_values[0]:>6.4f}")

for i in range(num_steps):
    # 1. Advance the simulation by one step
    simulator.forward()

    # 2. Finalize the step by updating the state variables
    # !! Important: Transition *before* reading the new value for storage !!
    simulator.transition()

    # 3. Store results for plotting
    current_time = main_system.clock.t.value # Time after transition
    times[i+1] = current_time
    health_values[i+1] = main_system.outer_layer.health.value
    functionality_values[i+1] = main_system.outer_layer.functionality.value

    # 4. Define Variable for meteorite impact value (separate from health)
    meteorite_impact_value = Variable(name="meteorite_impact_value", value=0.0, track=True) # Track if saving later

    # 5. Function to Calculate Impact Value for the current step
    @make_function(meteorite_impact_value)
    def calc_meteorite_impact(current_time=clock.t):
        """Calculates random meteorite impact value based on time."""
        t = current_time
        # Check if time is approx a multiple of interval (robust to small float errors)
        # Using int(round(t)) assumes dt is reasonably small compared to interval
        if t > 0 and abs(round(t) % impact_interval) < (simulation_dt / 2.0):
             # Generate random value
             impact_val = random.uniform(min_impact_value, max_impact_value)
             # print(f"DEBUG: Impact generated at t={t:.1f}, value={impact_val:.4f}") # Optional debug print
             return impact_val
        else:
            # No impact this step
            return 0.0
        
    if (i + 1) % 50 == 0 or i == num_steps - 1:
        print(f"Time: {main_system.clock.t.value:>6.2f} hr | "
            f"Outer Layer Health: {main_system.outer_layer.health.value:>6.4f} | "
            f"Functionality: {main_system.outer_layer.functionality.value:>6.4f}")


print("--- Simulation Finished ---")

# --- Final State ---
final_time = times[-1]
final_health = health_values[-1]
final_func = functionality_values[-1]

print(f"\nFinal State at Time = {final_time:.2f} hours:")
print(f"  Outer Layer Health = {final_health:.4f}")
print(f"  Outer Layer Functionality = {final_func:.4f}")

# --- Plotting Results ---
print(f"\n--- Generating Plot ---")
fig, ax = plt.subplots(figsize=(10, 6))

ax.plot(times, health_values, label='Outer Layer Health', linestyle='-', markersize=4)
# ax.plot(times, functionality_values, label='Outer Layer Functionality', linestyle='--', markersize=4)

ax.set_xlabel(f"Time ({main_system.clock.t.units})")
ax.set_ylabel("Value (Unitless)")
ax.set_title(f"Habitat Outer Layer Simulation (Damage Rate: {material_aging_rate_param} /hr)")
ax.legend()
ax.grid(True)
ax.set_ylim(0, 1.1) # Set y-axis limits for better visualization (0 to 110%)

try:
    plt.savefig(plot_output_file)
    print(f"Plot saved'")
except Exception as e:
    print(f"Error saving plot: {e}")

plt.show() # Display the plot

print("\n--- Script Complete ---")