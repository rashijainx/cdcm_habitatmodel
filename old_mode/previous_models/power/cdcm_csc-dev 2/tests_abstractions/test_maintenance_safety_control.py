"""Model implementing a safety-control on ETCS

Author:
    R Murali Krishnan

Date: 
    9/21/2023

"""


from cdcm import *
from cdcm_csc import *
from test_systems import make_etcs_maintenance
from cdcm_csc_systems import make_inventory, maintain

from datetime import datetime
import matplotlib.pyplot as plt
from collections import defaultdict


start_time = datetime(2000, 1, 12)
time_steps = 150

with System(name="sos") as sos:

    clock = make_clock(dt=1.0, units="hours")

    # ETCS system
    etcs = make_etcs_maintenance(clock, "moon", 0.0, 0.0, start_time, time_steps)

    # Inventory system
    inventory = make_inventory(tool_file_path="data/etcs_tools.yaml",
                                consumables_file_path="data/etcs_consumables.yaml")


etcs.forward()

g = make_pyvis_graph(etcs)
try:
    g.show("run_etcs_maintenance.html", notebook=False)
except:
    g.show("run_etcs_maintenance.html")

# Simulate for 150 hours.
saver = SimulationSaver("run_etcs_maintenance.h5", sos, time_steps, True)

# Simulator for coordinating events
model = Simulator(sos)

# Algorithm damag at 15 hrs
# model.add_event(15, change_value(etcs.controller.human_updates_algorithm.health, 0.95))

# Actuator power is damaged at 50 hr
# model.add_event(50, swtich_binary_value(etcs.controller.actuator_power.health))

# 60% per year
model.add_event(75, change_value(etcs.external_dust_rate, 14 * 5.0 / (24 * 365)))
# model.add_event(110, change_value(etcs.external_dust_rate, 5.0 / (24 * 365)))

# Maintain `etcs.controller.actuator_dust` :: Component
dusty_component = etcs.controller.dust
for i in range(1, time_steps, 5):
    model.add_event(i, maintain(dusty_component, inventory, 0.97, simulator=model))

inventory_log = defaultdict(list)

for i in range(time_steps):
    model.forward()
    saver.save()
    model.transition()
    inventory_log['de_duster'].append(inventory.tool_qty('de_duster'))
    inventory_log['end_effector_grasp_hard'].append(inventory.tool_qty('end_effector_grasp_hard'))
    inventory_log['actuator_dust_lru'].append(inventory.consumable_qty('actuator_dust_lru'))
    inventory_log['self_seal_barrier'].append(inventory.consumable_qty('self_seal_barrier'))

print("ovn!!") 
# quit()

# System states
fig, ax = plt.subplots(nrows=2, ncols=2)
ax[0, 0].plot(
    saver.file_handler["/sos/clock/t"][:],
    saver.file_handler["/sos/etcs/controller/power/health"][:],
)
ax[0, 0].set(ylabel="Actuator Power (Health)")
ax[0, 1].plot(
    saver.file_handler["/sos/clock/t"][:],
    saver.file_handler["/sos/etcs/controller/human_updates_algorithm/health"][:],
)
ax[0, 1].set(ylabel="Controller Algorithm (Health)")
ax[1, 0].plot(
    saver.file_handler["/sos/clock/t"][:],
    saver.file_handler["/sos/etcs/controller/dust/health"][:],
)
ax[1, 0].set(ylabel="Controller Actuator (Dust)")
ax[1, 1].plot(
    saver.file_handler["/sos/clock/t"][:],
    saver.file_handler["/sos/etcs/controller/functionality"][:],
)
ax[1, 1].set(ylabel="Controller Functionality")
fig.tight_layout()
# plt.savefig("controller_functionality_no_inventory.png", dpi=300)

# Inventory Logs
fig, ax = plt.subplots(nrows=2, ncols=2)
ax[0, 0].plot(
    saver.file_handler["/sos/clock/t"][:],
    inventory_log['de_duster'],
)
ax[0, 0].set(ylabel="De-Duster\n(Tool)")
ax[0, 1].plot(
    saver.file_handler["/sos/clock/t"][:],
    inventory_log['end_effector_grasp_hard'],
)
ax[0, 1].set(ylabel="Hard-Grasp End-Effector\n(Tool)")
ax[1, 0].plot(
    saver.file_handler["/sos/clock/t"][:],
    inventory_log['actuator_dust_lru'],
)
ax[1, 0].set(ylabel="Actuator Dust LRU\n(Consumables)")
ax[1, 1].plot(
    saver.file_handler["/sos/clock/t"][:],
    inventory_log['self_seal_barrier'],
)
ax[1, 1].set(ylabel="Self Seal Barrier\n(Consumables)")
fig.tight_layout()
# plt.savefig("controller_functionality_inventory_no_inventory.png", dpi=300)
plt.show()

