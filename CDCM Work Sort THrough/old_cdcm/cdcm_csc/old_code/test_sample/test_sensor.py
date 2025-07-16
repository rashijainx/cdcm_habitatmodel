import numpy as np
import matplotlib.pyplot as plt



from cdcm_constructs import *
from cdcm_habitat import *
from cdcm_utils import extract_data_from_saver, make_pyvis_graph

time_steps = 100

with System(name="system") as system:

    clock = make_clock(dt=1.0, units="hours")

    T_in = Variable(
        name="T_in",
        value=0.0
    )

    @make_function(T_in)
    def calc_T_in(
        time=clock.t
    ):
        return np.sin(2 * np.pi * time / time_steps) + 25

    sigma = Parameter(
        name="sigma",
        value=0.2,
        description="Signal to noise ratio"
    )

    theta = Parameter(
        name="theta",
        value=0.,
        description="Sensor threshold"
    )

    drift = State(
        name="drift",
        value=0.0,
        description="Drift of the sensor"
    )

    @make_function(drift)
    def calc_drift_sensor(
        d=drift,
        t=theta,
        dt=clock.dt
    ):
        return dt * t + d

    T_m = Variable(
        name="T_m",
        value=0.0,
        description="Measured temperature"
    )

    @make_function(T_m)
    def calc_T_m(
        T_in=T_in,
        drift=drift,
        sigma=sigma
    ):
        return T_in + sigma * np.random.randn() + drift

file_name = __file__.split("/")[-1][:-3]

system.forward()
print(system)

# Creating pyvis graph
print(">.. Pyvis is making the HTML file")
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
    "T_in": "/system/T_in",
    "T_m": "/system/T_m"
}

data = extract_data_from_saver(saver, _map)

fig, ax = plt.subplots(nrows=1)
ax.plot(data["t"], data["T_in"], label="Actual", color="black")
ax.plot(data["t"], data["T_m"], label="Measured", color="red")
ax.set(xlabel="Time [hours]", ylabel="Temperature [°C]")
ax.legend()

plt.show()
