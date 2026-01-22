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
    status: int, #-1 for Charging, 0 for Idle, 1 for Discharging
    initial_charge: float, 
    discharge_rate: float,
    charge_rate: float,
    self_discharge_rate: float, 
    age_rate: float, 
    health_threshold: float,
    damage_threshold: float,
): 
    with System (name=name) as battery: 

        age_rate = Variable(
            name="age_rate", 
            value=age_rate
        )

        hardware = make_component(
            name="hardware",
            aging_rate=age_rate,
            dt=clock.dt,
            Ed=damage_threshold
        )

        health_threshold = Variable(
            name="health_threshold", 
            value=health_threshold
        )

        discharge_rate = Variable(
            name="discharge_rate", 
            value=discharge_rate
        )

        charge_rate = Variable(
            name="charge_rate", 
            value=charge_rate
        )

        status = Variable(
            name="status", 
            value=status
        )

        chargeordischarge = State(
            name="chargeordischarge", 
            value=initial_charge
        )

        max_charge = Variable(
            name="max_charge", 
            value=initial_charge
        )

        self_discharge = Variable(
            name="self_discharge_rate", 
            value=self_discharge_rate
        )

        @make_function(chargeordischarge)
        def calc_battery_charge(
            C=chargeordischarge,
            Cmax=max_charge,
            s=status,
            dr=discharge_rate, 
            cr=charge_rate,
            dt=clock.dt,
            k_self=self_discharge,
        ): 
            if s == 1:  # Battery is discharging
                return max(0, C - dr*dt)
            elif s==-1:  # Battery is charging
                return min(Cmax, C + cr*dt)
            else:  # Battery is not charging or dischargin
                return C - k_self * dt
        
        def fn_battery_functionality(
            hardware,
            health_threshold,
            charge,
        ) -> float:
            if hardware > health_threshold:
                return charge
            else:
                return 0.0
            
        battery_functinality_inputs = (
            hardware,
            health_threshold,
            chargeordischarge,
        )

        battery_functionality = make_functionality(
            *battery_functinality_inputs,
            functionality_func=fn_battery_functionality, 
            name="provide_power",
        ) 

        return battery


# Simulation parameters

time_steps = 500

if __name__ == "__main__":

    with System(name="system") as system:

        clock = make_clock(dt=1.0, units="hours")

        status = 1
        initial_charge = 100.0
        discharge_rate = 0.1
        charge_rate = 0.05
        self_discharge_rate = 0.001
        aging_rate = 10/(24*365)
        health_threshold = 0.5
        damage_threshold = 0.015

        battery = make_battery(
            "battery",
            clock, 
            status,
            initial_charge,
            discharge_rate,
            charge_rate,
            self_discharge_rate,
            aging_rate,
            health_threshold,
            damage_threshold,
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

    model.add_event(250, change_value(system.battery.status, 0))
    model.add_event(275, change_value(system.battery.status, -1))

    for i in range(time_steps):
        model.forward()
        saver.save()
        model.transition()

    _map = {
        "t": "/system/clock/t",
        "health": "/system/battery/hardware/functionality",
        "chargeordischarge": "/system/battery/chargeordischarge",
        "charge_output": "/system/battery/provide_power"
        }

    data = extract_data_from_saver(saver, _map)

    fig, axs = plt.subplots(nrows=3)

    axs[0].plot(data["t"], data["health"])
    axs[0].set(ylabel="Health")

    axs[1].plot(data["t"], data["chargeordischarge"])
    axs[1].set(ylabel="Charge")

    axs[2].plot(data["t"], data["charge_output"])
    axs[2].set(ylabel="Charge Output")


    plt.show()
    print("~~ovn!")