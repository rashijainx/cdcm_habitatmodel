# energy_storage.py — CDCM battery builders
# Exports:
#   - make_battery_base
#   - make_nonrechargeable_battery
#   - make_rechargeable_battery

__all__ = [
    "make_battery_base",
    "make_nonrechargeable_battery",
    "make_rechargeable_battery",
]

from cdcm import *
from cdcm_abstractions import *
from cdcm_utils import *

# Plot Libraries 
import matplotlib.pyplot as plt

def make_battery_base(
    name: str,
    *,
    clock: System,
    mode: int,
    initial_charge: float,
    capacity: float,
    discharge_rate: float,
    charge_rate: float,
    self_discharge_rate: float = 0.0,
    aging_rate: float = 0.0,
    health_threshold: float = 0.5,
    damage_threshold: float = 0.015,
):
    
    with System(name=name) as battery:
        # --- Params / Vars ---
        age_rate_v   = Variable(name="age_rate", value=aging_rate)
        mode_v       = Variable(name="mode", value=mode)  # -1/0/1
        dr_v         = Variable(name="discharge_rate", value=discharge_rate)
        cr_v         = Variable(name="charge_rate", value=charge_rate)
        kself_v      = Variable(name="self_discharge_rate", value=self_discharge_rate)
        hth_v        = Variable(name="health_threshold", value=health_threshold)

        # --- Hardware block (health/aging) ---
        hardware = make_component(
            name="hardware",
            aging_rate=age_rate_v,
            dt=clock.dt,
            Ed=damage_threshold,
        )

        # --- States ---
        C_max  = State(name="capacity_max", value=max(0.0, capacity))
        chargeordischarge = State(name="chargeordischarge", value=min(max(0.0, initial_charge), max(0.0, capacity)))

        # --- Derived: SoC ---
        soc = Variable(name="soc", value=(0.0 if C_max.value <= 0.0 else chargeordischarge.value / C_max.value))

        @make_function(soc)
        def calc_soc(Q=chargeordischarge, Cmax=C_max):
            return 0.0 if Cmax <= 0.0 else max(0.0, min(1.0, Q / Cmax))

        # --- Charge transition ---
        @make_function(chargeordischarge)
        def calc_charge(
            Q=chargeordischarge,
            m=mode_v,
            dr=dr_v,
            cr=cr_v,
            k_self=kself_v,
            dt=clock.dt,
            Cmax=C_max,
        ):
            """
            Commanded change:
            m = +1  discharge:  dQ_cmd = -dr * dt
            m = -1  charge:     dQ_cmd = +cr * dt
            m =  0  idle:       dQ_cmd = 0
            Passive self-discharge always: dQ_self = -k_self * Q * dt
            Clamp to [0, Cmax]
            """
            # If charge_rate == 0 (non-rechargeable), ignore m=-1
            m_eff = m if cr > 0.0 else (0 if m == -1 else m)

            if m_eff == 1:        # discharge
                dQ_cmd = -dr * dt   # <-- fix: negative
            elif m_eff == -1:     # charge
                dQ_cmd = +cr * dt
            else:                 # idle
                dQ_cmd = 0.0

            dQ_self = -k_self * Q * dt
            Q_next = Q + dQ_cmd + dQ_self

            if Q_next < 0.0: Q_next = 0.0
            if Q_next > Cmax: Q_next = Cmax
            return Q_next

        # --- Functionality gate (your pattern) ---
        def fn_battery_functionality(hardware_val, health_th, Q):
            if hardware_val > health_th and Q > 0.0:
                return Q  # simple "available energy" proxy
            return 0.0

        make_functionality(
            hardware, hth_v, chargeordischarge,
            functionality_func=fn_battery_functionality,
            name="provide_power",
        )

        return battery


# ------------------ Thin wrappers ------------------

def make_nonrechargeable_battery(
    name: str,
    *,
    clock: System,
    status: int,                    # 0 = idle, 1 = discharge (matches your first script)
    initial_charge: float,
    discharge_rate: float,
    self_discharge_rate: float,
    aging_rate: float,
    health_threshold: float,
    damage_threshold: float,
    capacity: float = None,         # default to initial_charge for clamping
):
    if capacity is None:
        capacity = max(0.0, float(initial_charge))
    mode = 1 if int(status) == 1 else 0  # map status->mode
    return make_battery_base(
        name,
        clock=clock,
        mode=mode,
        initial_charge=initial_charge,
        capacity=capacity,
        discharge_rate=discharge_rate,
        charge_rate=0.0,                 # disable charging path
        self_discharge_rate=self_discharge_rate,
        aging_rate=aging_rate,
        health_threshold=health_threshold,
        damage_threshold=damage_threshold,
    )


def make_rechargeable_battery(
    name: str,
    *,
    clock: System,
    status: int,                    # -1 = charge, 0 = idle, 1 = discharge (matches your second script)
    initial_charge: float,
    discharge_rate: float,
    charge_rate: float,
    self_discharge_rate: float,
    aging_rate: float,
    health_threshold: float,
    damage_threshold: float,
    capacity: float = None,
):
    if capacity is None:
        capacity = max(0.0, float(initial_charge))
    mode = int(status)
    # sanitize to {-1,0,1}
    if mode not in (-1, 0, 1):
        mode = 0
    return make_battery_base(
        name,
        clock=clock,
        mode=mode,
        initial_charge=initial_charge,
        capacity=capacity,
        discharge_rate=discharge_rate,
        charge_rate=charge_rate,
        self_discharge_rate=self_discharge_rate,
        aging_rate=aging_rate,
        health_threshold=health_threshold,
        damage_threshold=damage_threshold,
    )


# Simulation parameters

time_steps = 500

if __name__ == "__main__":

    with System(name="system") as system:

        clock = make_clock(dt=1.0, units="hours")

        status = 1
        initial_charge = 100.0
        capacity = 125.0
        discharge_rate = 0.1
        charge_rate = 0.05
        charge_rate = 0.05
        self_discharge_rate = 0
        aging_rate = 10/(24*365)
        health_threshold = 0.25
        damage_threshold = 0.015

        nbattery = make_nonrechargeable_battery(
            "nbattery",
            clock=clock, 
            status=status,
            initial_charge=initial_charge,
            discharge_rate=discharge_rate,
            self_discharge_rate=self_discharge_rate,
            aging_rate=aging_rate,
            health_threshold=health_threshold,
            damage_threshold=damage_threshold,
        ) 

        cbattery = make_rechargeable_battery(
            "cbattery",
            clock=clock,
            status=status,
            initial_charge=initial_charge,
            discharge_rate=discharge_rate,
            charge_rate=charge_rate,
            self_discharge_rate=self_discharge_rate,
            aging_rate=aging_rate,
            health_threshold=health_threshold,
            damage_threshold=damage_threshold,
            capacity=capacity,
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

    model.add_event(20, change_value(system.nbattery.mode, 0))
    model.add_event(275, change_value(system.nbattery.mode, 1))

    model.add_event(275, change_value(system.cbattery.mode, -1))

    for i in range(time_steps):
        model.forward()
        saver.save()
        model.transition()

    _map = {
        "t": "/system/clock/t",
        "nhealth": "/system/nbattery/hardware/functionality",
        "nchargeordischarge": "/system/nbattery/chargeordischarge",
        "ncharge_output": "/system/nbattery/provide_power",

        "chealth": "/system/cbattery/hardware/functionality",
        "cchargeordischarge": "/system/cbattery/chargeordischarge",
        "ccharge_output": "/system/cbattery/provide_power"
        }

    data = extract_data_from_saver(saver, _map)

    fig, axs = plt.subplots(nrows=3)

    axs[0].plot(data["t"], data["nhealth"])
    axs[0].set(ylabel="Health")

    axs[1].plot(data["t"], data["nchargeordischarge"])
    axs[1].set(ylabel="Charge")

    axs[2].plot(data["t"], data["ncharge_output"])
    axs[2].set(ylabel="Charge Output")

    fig, axs = plt.subplots(nrows=3)

    axs[0].plot(data["t"], data["chealth"])
    axs[0].set(ylabel="Health")

    axs[1].plot(data["t"], data["cchargeordischarge"])
    axs[1].set(ylabel="Charge")

    axs[2].plot(data["t"], data["ccharge_output"])
    axs[2].set(ylabel="Charge Output")


    plt.show()
    print("~~ovn!")