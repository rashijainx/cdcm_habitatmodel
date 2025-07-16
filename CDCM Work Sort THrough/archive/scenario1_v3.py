from cdcm import *
from cdcm_utils import *
from cdcm_abstractions import *


# Standard Python/Data Science libraries
import matplotlib.pyplot as plt
import numpy as np
import random


# --- Simulation Parameters ---
simulation_total_time = 131400 # hours (15 years)
simulation_dt = 1.0           # hours (timestep)
epsilon = simulation_dt / 2.0 # Small time offset for reset event

# --- Material Configuration ---
material_data_file = "material_properties.yaml"
target_material_name = "Cast_Regolith"

# --- Small Meteorite Impact Parameters (Events) ---
small_impact_interval = 100.0 # hours
large_impact_interval = 60000.0 # hours


# --- Output File Names ---
pyvis_output_file = "habitat_resistance_graph.html"

# --- Load Material Data ---
print(f"--- Loading Material Data from '{material_data_file}' ---")
try:
    material_data = parse_yaml(material_data_file)
    if 'materials' not in material_data or target_material_name not in material_data['materials']:
        raise KeyError(f"Material '{target_material_name}' not found.")
    selected_material_props = material_data['materials'][target_material_name]
    loaded_base_degradation_rate = selected_material_props['aging_rate']
    min_small_impact_value = selected_material_props.get('min_small_impact', 0.0)
    max_small_impact_value = selected_material_props.get('max_small_impact', 0.0)
    min_large_impact_value = selected_material_props.get('min_large_impact', 0.0)
    max_large_impact_value = selected_material_props.get('max_large_impact', 0.0)
    material_description = selected_material_props.get('description', 'No description.')
    print(f"Loaded properties for: '{target_material_name}' (Base Deg. Rate: {loaded_base_degradation_rate} /hr)")
except Exception as e:
    print(f"ERROR loading material data: {e}")
    exit()

# --- Define the System using the 'with' context manager ---
print("\n--- Defining System ---")
with System(name="habitat_simulation") as main_system:

    # 1. Create the simulation clock
    clock = make_clock(dt=simulation_dt, units="hours")
    print(f"Clock created with dt={clock.dt.value} {clock.dt.units}")

    # 2. Define the material base degradation rate (parameter)
    material_base_rate_param = make_node(
        f"P:material_base_rate:{loaded_base_degradation_rate}:1/hour",
        description=f"Base degradation rate for {target_material_name}."
    )
    print(f"Material base rate parameter created: {material_base_rate_param.name} = {material_base_rate_param.value}")

    # 3. Create the Outer Structure Layer Component (Health/Functionality)
    #    Health degradation depends ONLY on the material_base_rate_param.
    outer_layer = make_component(
        name="outer_layer",
        dt=clock.dt,
        nominal_health=1.0,
        health_damage_rate=material_base_rate_param, # Health uses base rate
        nominal_functionality=1.0,
        description="The outer structural layer of the habitat (base degradation)."
    )
    print(f"Component '{outer_layer.name}' created.")

    # 4. Define Variable for SMALL impact value WHEN THE EVENT OCCURS
    small_impact_value_event = Variable(name="small_impact_value_event", value=0.0, track=True)

    # 5. Define Variable for LARGE impact value WHEN THE EVENT OCCURS
    large_impact_value_event = Variable(name="large_impact_value_event", value=0.0, track=True)

    # 6. Define NEW State variable for Impact Resistance
    impact_resistance_variable = State(name="impact_resistance_variable", value=1.0, track=True,)

    # 7. Define Transition function for Impact Resistance State
    @make_function(impact_resistance_variable) # Decorator makes this a Transition function
    def update_impact_resistance(
        impact=impact_resistance_variable,
        small_impact=small_impact_value_event,       # Depends on small impact event variable
        large_impact=large_impact_value_event        # Depends on large impact event variable
    ):
        """Decreases resistance based on impact values from events."""
        # Decrease resistance by the sum of impacts (only one should be non-zero near an event time)
        next_resistance = impact - small_impact - large_impact
        # Ensure resistance doesn't go below zero
        return max(0.0, next_resistance)
    
    pressure = Variable(name="pressure", value=1.0, track=True)

    @make_function(pressure)
    def calc_pressure():
        return 20.0
    #     impact=impact_resistance_variable,
    #     # outgassing_tolerance=0.1,
    # ): 
    #     if impact.value > 0.9: 
    #         return 1.0
    #     else: 
    #         return 0.0
        
    print(f"Pressure '{pressure.value}'")


print("\n--- System Definition Complete ---")

# --- Generate Pyvis Visualization ---
print(f"\n--- Generating Pyvis graph ---")
try:
    pyvis_graph = make_pyvis_graph(main_system)
    pyvis_graph.save_graph(pyvis_output_file)
    print(f"Pyvis graph saved to ")
except Exception as e:
    print(f"Error generating Pyvis graph: {e}")

# --- Set up the Simulator ---
print("\n--- Initializing Simulator ---")
simulator = Simulator(system=main_system)
print("Simulator created.")

# --- Define Event Functions --- (Same as before)
def reset_small_impact_value():
    main_system.small_impact_value_event.value = 0.0
def trigger_small_meteorite_impact():
    current_time = main_system.clock.t.value
    impact_val = random.uniform(min_small_impact_value, max_small_impact_value)
    main_system.small_impact_value_event.value = impact_val
    simulator.add_event(current_time + epsilon, reset_small_impact_value)
    simulator.add_event(current_time + small_impact_interval, trigger_small_meteorite_impact)
def reset_large_impact_value():
    main_system.large_impact_value_event.value = 0.0
def trigger_large_meteorite_impact():
    current_time = main_system.clock.t.value
    impact_val = random.uniform(min_large_impact_value, max_large_impact_value)
    main_system.large_impact_value_event.value = impact_val
    simulator.add_event(current_time + epsilon, reset_large_impact_value)
    simulator.add_event(current_time + large_impact_interval, trigger_large_meteorite_impact)

# --- Schedule the FIRST Impact Events --- (Same as before)
print(f"\n--- Scheduling First Small Impact Event at t={small_impact_interval:.1f} ---")
simulator.add_event(small_impact_interval, trigger_small_meteorite_impact)
print(f"--- Scheduling First Large Impact Event at t={large_impact_interval:.1f} ---")
simulator.add_event(large_impact_interval, trigger_large_meteorite_impact)

# --- Prepare Data Storage for Plotting ---
num_steps = int(simulation_total_time / simulation_dt)
times = np.zeros(num_steps + 1)
health_values = np.zeros(num_steps + 1)
functionality_values = np.zeros(num_steps + 1)
small_impact_marker = np.zeros(num_steps + 1)
large_impact_marker = np.zeros(num_steps + 1)
impact_resistance_values = np.zeros(num_steps + 1)
# structure_integrity_values = np.zeros(num_steps + 1) # Store the new variable

# Store initial state (t=0)
times[0] = main_system.clock.t.value
health_values[0] = main_system.outer_layer.health.value
# --- Initial Calculation ---
simulator.forward() # Calculate initial values based on t=0 inputs
functionality_values[0] = main_system.outer_layer.functionality.value
small_impact_marker[0] = main_system.small_impact_value_event.value # 0
large_impact_marker[0] = main_system.large_impact_value_event.value # 0
impact_resistance_values[0] = main_system.impact_resistance_variable.value # 0
# structure_integrity_values[0] = main_system.structure_integrity.value # Should be 0 (health * 0)

# print(f"\n--- Starting Simulation: {num_steps} steps ({simulation_total_time/24/365.25:.1f} years)---")
# print(f"Time: {times[0]:>8.2f} hr | Health: {health_values[0]:>6.4f} | ResistVar: {impact_resistance_values[0]:>6.4f} | Func: {functionality_values[0]:>6.4f} | StructInt: {structure_integrity_values[0]:>6.4f} | Sm.Imp: {small_impact_marker[0]:>6.4f} | Lg.Imp: {large_impact_marker[0]:>6.4f}")


print(f"\n--- Starting Simulation: {num_steps} steps ({simulation_total_time/24/365.25:.1f} years)---")
print(f"Time: {times[0]:>8.2f} hr | Health: {health_values[0]:>6.4f} | ResistVar: {impact_resistance_values[0]:>6.4f} | Func: {functionality_values[0]:>6.4f} | Sm.Imp: {small_impact_marker[0]:>6.4f} | Lg.Imp: {large_impact_marker[0]:>6.4f}")

small_impact_event_count = 0
large_impact_event_count = 0
for i in range(num_steps):
    # 1. Advance simulation (runs events, calculates next states for health, func, AND resistance)
    simulator.forward()

    # Store event variable values *after* forward potentially modified them
    current_small_impact_val = main_system.small_impact_value_event.value
    current_large_impact_val = main_system.large_impact_value_event.value
    small_impact_marker[i+1] = current_small_impact_val
    large_impact_marker[i+1] = current_large_impact_val
    if current_small_impact_val > 0:
        small_impact_event_count += 1
    if current_large_impact_val > 0:
        large_impact_event_count += 1

    # 2. Finalize state transitions (updates health AND resistance)
    simulator.transition()

    # 3. Store results AFTER transition
    current_time = main_system.clock.t.value
    times[i+1] = current_time
    health_values[i+1] = main_system.outer_layer.health.value
    functionality_values[i+1] = main_system.outer_layer.functionality.value
    impact_resistance_values[i+1] = main_system.impact_resistance_variable.value # Store resistance state

    # 4. Print status periodically
    if (i + 1) % (24 * 30 * 12) == 0 or i == num_steps - 1: # Approx every year
         print(f"Time: {current_time:>8.2f} hr | Health: {health_values[i+1]:>6.4f} | Resist: {impact_resistance_values[i+1]:>6.4f} | Func: {functionality_values[i+1]:>6.4f} | Sm.Imp: {current_small_impact_val:>6.4f} | Lg.Imp: {current_large_impact_val:>6.4f}")

print("--- Simulation Finished ---")
print(f"Total steps where small impact variable > 0: {small_impact_event_count}")
print(f"Total steps where large impact variable > 0: {large_impact_event_count}")

# --- Final State ---
final_time = times[-1]
final_health = health_values[-1]
final_func = functionality_values[-1]
final_resistance = impact_resistance_values[-1]
print(f"\nFinal State at Time = {final_time:.2f} hours:")
print(f"  Outer Layer Health = {final_health:.4f}")
print(f"  Outer Layer Functionality = {final_func:.4f}")
print(f"  Impact Resistance = {final_resistance:.4f}")

# --- Plotting Results (Health & Functionality) --- (Same as before)
print(f"\n--- Generating Health/Functionality Plot ---")
fig_health, ax_health = plt.subplots(figsize=(12, 6))
ax_health.plot(times, health_values, label='Outer Layer Health', linestyle='-', color='tab:red')
ax_health.plot(times, functionality_values, label='Outer Layer Functionality', linestyle='--', color='tab:orange')
ax_health.set_xlabel(f"Time ({main_system.clock.t.units})")
ax_health.set_ylabel("Value (Unitless)")
ax_health.set_title(f"Habitat Simulation: '{target_material_name}' (Base Rate: {loaded_base_degradation_rate:.2e} /hr)")
ax_health.legend()
ax_health.grid(True)
ax_health.set_ylim(-0.05, 1.1)
try:
    plt.savefig(plot_output_file)
    print(f"Health/Functionality plot saved ")
except Exception as e:
    print(f"Error saving health/functionality plot: {e}")

# --- Plotting Results (Small Meteorite Impact Event Variable) --- (Same as before)
print(f"\n--- Generating Small Impact Event Variable Plot ---")
fig_small_impact, ax_small_impact = plt.subplots(figsize=(12, 4))
markerline, stemlines, baseline = ax_small_impact.stem(times, small_impact_marker,
                                                 linefmt='tab:blue',
                                                 label='Small Impact Event Value')
plt.setp(stemlines, 'linewidth', 0.5); plt.setp(markerline, 'markersize', 2)
ax_small_impact.set_xlabel(f"Time ({main_system.clock.t.units})"); ax_small_impact.set_ylabel("Impact Value")
ax_small_impact.set_title(f"Simulated Small Meteorite Impact Events (Interval ~{small_impact_interval}hr)")
ax_small_impact.grid(True); ax_small_impact.set_ylim(bottom=-0.001, top=max_small_impact_value * 1.2)
try:
    plt.savefig(small_impact_plot_output_file)
    print(f"Small impact event variable plot saved ")
except Exception as e:
    print(f"Error saving small impact plot: {e}")

# --- Plotting Results (Large Meteorite Impact Event Variable) --- (Same as before)
print(f"\n--- Generating Large Impact Event Variable Plot ---")
fig_large_impact, ax_large_impact = plt.subplots(figsize=(12, 4))
markerline, stemlines, baseline = ax_large_impact.stem(times, large_impact_marker,
                                                 linefmt='tab:green',
                                                 label='Large Impact Event Value')
plt.setp(stemlines, 'linewidth', 1.0); plt.setp(markerline, 'markersize', 4)
ax_large_impact.set_xlabel(f"Time ({main_system.clock.t.units})"); ax_large_impact.set_ylabel("Impact Value")
ax_large_impact.set_title(f"Simulated Large Meteorite Impact Events (Interval ~{large_impact_interval}hr)")
ax_large_impact.grid(True); ax_large_impact.set_ylim(bottom=-0.01, top=max_large_impact_value * 1.1)
try:
    plt.savefig(large_impact_plot_output_file)
    print(f"Large impact event variable plot saved ")
except Exception as e:
    print(f"Error saving large impact plot: {e}")

# --- Plotting Results (Impact Resistance State) --- (NEW PLOT)
print(f"\n--- Generating Impact Resistance Plot ---")
fig_resistance, ax_resistance = plt.subplots(figsize=(12, 6))
ax_resistance.plot(times, impact_resistance_values, label='Impact Resistance State', linestyle='-', color='purple')
ax_resistance.set_xlabel(f"Time ({main_system.clock.t.units})")
ax_resistance.set_ylabel("Resistance Value (Unitless)")
ax_resistance.set_title(f"Simulated Impact Resistance State Over Time")
ax_resistance.legend()
ax_resistance.grid(True)
ax_resistance.set_ylim(-0.05, 1.1) # Start at 1.0, decrease towards 0
try:
    plt.savefig(resistance_plot_output_file)
    print(f"Impact resistance state plot saved")
except Exception as e:
    print(f"Error saving resistance plot: {e}")


# # --- Plotting Results (Structure Integrity) --- (NEW PLOT)
# print(f"\n--- Generating Structure Integrity Plot ---")
# fig_struct, ax_struct = plt.subplots(figsize=(12, 6))
# ax_struct.plot(times, structure_integrity_values, label='Structure Integrity (Health * Impact Mag)', linestyle='-', color='cyan')
# ax_struct.set_xlabel(f"Time ({main_system.clock.t.units})")
# ax_struct.set_ylabel("Integrity Value")
# ax_struct.set_title(f"Simulated Structure Integrity (Health * Impact Magnitude)")
# ax_struct.legend()
# ax_struct.grid(True)
# ax_struct.set_ylim(bottom=-0.01) # Should only be positive
# try:
#     plt.savefig(structure_integrity_plot_output_file)
#     print(f"Structure integrity plot saved to '{os.path.abspath(structure_integrity_plot_output_file)}'")
# except Exception as e:
#     print(f"Error saving structure integrity plot: {e}")


plt.show() # Display all plots

print("\n--- Script Complete ---")
