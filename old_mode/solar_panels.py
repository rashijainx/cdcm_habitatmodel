
__all__ = [
    "make_solar_panel",
]

from datetime import datetime, timedelta

from cdcm import *
from cdcm_abstractions import *
from cdcm_utils import *
from cdcm_utils.solar_irradiation import get_insolation_ephemeris

from exterior_variables import *

# Plot Libraries 
import matplotlib.pyplot as plt

def make_solar_panels(
    name: str,
    clock: System,
    mode: int,
    capacity: float,
    solar_irradiance: variable,
    aging_rate: float=0.0,
    health_threshold: float=0.5,
    damage_threshold: float=0.015,
):
    
    with System(name=name) as solar_panels:
        
        age_rate_v = Variable(name="age_rate", value=aging_rate)
        mode_v = Variable(name="mode", value=mode) # 1 (on) /0 (off)
        C_v = Variable(name="capacity", value=capacity)
        hth_v = Variable(name="health_threshold", value=health_threshold)

        hardware = make_component(
            name="hardware",
            aging_rate=age_rate_v,
            dt=clock.dt,
            Ed=damage_threshold,
        )

        # --- Functionality gate ---
        def fn_solar_panel_functionality(hardware_val, health_th, SI, mode, C):
            if hardware_val > health_th and SI > 0.25 and mode == 1:
                return (C*SI - C*0.25)
            else: 
                return 0.0

        solar_panel_functionality_inputs = (
            hardware,
            hth_v,
            solar_irradiance,
            mode_v,
            C_v
        )

        make_functionality(
            *solar_panel_functionality_inputs, 
            functionality_func=fn_solar_panel_functionality,
            name="generate_power"
        )
    
        return solar_panels
    

# Simulation parameters

time_steps = 500
start_time = datetime(2025, 1, 1)

if __name__ == "__main__":

    with System(name="system") as system:

        clock = make_clock(dt=1.0, units="hours")
        sun = SolarIrradiance("sun", clock, start_time, time_steps)
        scaled_solar_irradiance = scale(sun.solar_irradiance, 1/1361.00, name="scaled_solar_irradiance")

        solar_panel = make_solar_panels(
            name="solar_panel",
            clock=clock,
            mode=1,
            capacity=20.0,
            solar_irradiance=scaled_solar_irradiance,
            aging_rate=0.01/(24*365),
            health_threshold=0.5,
            damage_threshold=0.015,
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

    for i in range(time_steps):
        model.forward()
        saver.save()
        model.transition()

    _map = {
        "t": "/system/clock/t",
        "sun": "/system/scaled_solar_irradiance",
        "health": "/system/solar_panel/hardware/functionality",
        "power_output": "/system/solar_panel/generate_power",
        }

    data = extract_data_from_saver(saver, _map)

    fig, axs = plt.subplots(nrows=3)

    axs[0].plot(data["t"], data["health"])
    axs[0].set(ylabel="Health")

    axs[1].plot(data["t"], data["power_output"])
    axs[1].set(ylabel="% Power Req")

    axs[2].plot(data["t"], data["sun"])
    axs[2].set(ylabel="Sun", xlabel="Time (hours)")

    plt.show()
    print("~~ovn!")

