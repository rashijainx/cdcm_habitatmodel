# Non-Rechargeable Battery 


# CDCM Execution Code Libraries 
from cdcm import * 
from cdcm_abstractions import *
from cdcm_utils import *

# Plot Libraries 
import matplotlib.pyplot as plt


def make_battery(
    name: str, 
    clock: System,
    status: int, 
    initial_charge: float, 
    discharge_rate: float,
    self_discharge_rate: float, 
): 
    with System (name=name) as battery: 

        discharge_rate = Variable(
            name="discharge_rate", 
            value=discharge_rate
        )

        status = Variable(
            name="status", 
            value=status
        )

        charge = State(
            name="charge", 
            value=initial_charge
        )

        self_discharge = Variable(
            name="self_discharge_rate", 
            value=self_discharge_rate
        )

        @make_function(charge)
        def calc_battery_charge(
            C=charge, 
            s=status,
            dr=discharge_rate, 
            dt=clock.dt,
            k_self=self_discharge, 
        ): 
            if s == 1:  # Battery is discharging
                return max(0, C - dr*dt)
            else:  # Battery is not discharging
                return C - k_self * dt
        
        return battery


# Simulation parameters

time_steps = 500

if __name__ == "__main__":

    with System(name="system") as system:

        clock = make_clock(dt=1.0, units="hours")

        status = 1
        initial_charge = 100.0
        discharge_rate = 0.1
        self_discharge_rate = 0.001

        battery = make_battery(
            "battery",
            clock, 
            status,
            initial_charge,
            discharge_rate,
            self_discharge_rate,
        ) 


    file_name = __file__.split("/")[-1][:-3]

    system.forward()
    print(system)

    print(">.. Pyvis is making the HTML file.")

    tcs_graph = make_pyvis_graph(system)
    try:
        tcs_graph.show(file_name + ".html", notebook=False)
    except:
        tcs_graph.show(file_name + ".html")
    print(">... done")

    saver = SimulationSaver(
        file_name + ".h5",
        system,
        max_steps=time_steps,
        overwrite=True
    )
    model = Simulator(system)

    model.add_event(10, change_value(system.battery.status, 0))
    model.add_event(250, change_value(system.battery.status, 1))

    for i in range(time_steps):
        model.forward()
        saver.save()
        model.transition()

    _map = {
        "t": "/system/clock/t",

        "charge": "/system/battery/charge",
        }

    data = extract_data_from_saver(saver, _map)

    fig, axs = plt.subplots(nrows=2)

    axs[0].plot(data["t"], data["charge"])
    axs[0].set(ylabel="Charge")


    plt.show()
    print("~~ovn!")