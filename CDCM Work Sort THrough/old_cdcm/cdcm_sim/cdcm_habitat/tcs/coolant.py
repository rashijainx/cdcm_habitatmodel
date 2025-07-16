"""Model of coolant

Author:
    Rashi Jain

Date:
    1/25/2024 |
    2/29/2024 | Pooled Coolant
"""
from cdcm import *
from cdcm_constructs import *
from typing import Optional, List

__all__ = ["make_coolant", 
           "make_pooled_coolant",]


def make_coolant(
    name: str,
    type: str, # standard, heatIN, heatOUT, pump
    container_insulate: NumOrVar,
    container_store: NumOrVar,
    valveOUT: System,
    plumbingIN: Optional[System[None]]=None,
    affect: Optional[Variable]=None,
) -> System:

    with System(name=name) as coolant:

        valveOUT_state = valveOUT.position

        if plumbingIN is not None:

            valveIN_state = plumbingIN.valve.position
            fluidIN_cont = plumbingIN.coolant.contamination
            fluidIN_vol = plumbingIN.coolant.volume
            fluidIN_pres = plumbingIN.coolant.pressure
            fluidIN_temp = plumbingIN.coolant.temperature

            volume = State(
                name="volume",
                value=1.0,
            )

            @make_function(volume)
            def calc_volume(
                container_store=container_store,
                connectOUT_state=valveOUT_state,
                connectIN_state=valveIN_state,
                fluidIN_vol=fluidIN_vol,
                volume=volume
            ):
                volume = container_store - connectOUT_state * \
                        volume + connectIN_state * fluidIN_vol
                return volume

            pressure = State(
                name="pressure",
                value=1.0,
            )

            if type == "heatIN" or type == "heatOUT" or type == "standard":
                @make_function(pressure)
                def calc_pressure(
                    container_store=container_store,
                    connectOUT_state=valveOUT_state,
                    connectIN_state=valveIN_state,
                    fluidIN_pres=fluidIN_pres,
                    pressure=pressure
                ):
                    pressure = container_store - connectOUT_state * \
                            pressure + connectIN_state * fluidIN_pres
                    return pressure
            elif type == "pump":
                @make_function(pressure)
                def calc_pressure(
                    container_store=container_store,
                    connectOUT_state=valveOUT_state,
                    connectIN_state=valveIN_state,
                    fluidIN_pres=fluidIN_pres,
                    pressure=pressure,
                    affect=affect,
                ):
                    # Incoming pressure does not affect if the pump functions
                    # above specified threshold
                    if affect >= 0.5:
                        pressure = container_store - connectOUT_state * \
                            pressure + connectIN_state
                    else: 
                        pressure = container_store - connectOUT_state * \
                            pressure + connectIN_state * fluidIN_pres
                    return pressure
            else: 
                raise ValueError("Invalid type")

            temperature = State(
                name="temperature",
                value=1.0,
            )

            if type == "heatIN":
                @make_function(temperature)
                def calc_temperature(
                    container_insulate=container_insulate,
                    connectOUT_state=valveOUT_state,
                    connectIN_state=valveIN_state,
                    fluidIN_temp=fluidIN_temp,
                    temperature=temperature,
                ):
                    temperature = (1 - container_insulate) - connectOUT_state * \
                            temperature + connectIN_state * fluidIN_temp
                    return temperature
            elif type == "heatOUT":
                @make_function(temperature)
                def calc_temperature(
                    container_insulate=container_insulate,
                    connectOUT_state=valveOUT_state,
                    connectIN_state=valveIN_state,
                    fluidIN_temp=fluidIN_temp,
                    temperature=temperature,
                    panel_loss=affect
                ):
                    temperature = panel_loss * (1 - container_insulate) - connectOUT_state * \
                            temperature + connectIN_state * fluidIN_temp
                    return temperature
            elif type == "standard" or type == "pump":
                @make_function(temperature)
                def calc_temperature(
                    container_insulate=container_insulate,
                    connectOUT_state=valveOUT_state,
                    connectIN_state=valveIN_state,
                    fluidIN_temp=fluidIN_temp,
                    temperature=temperature,
                ):
                    temperature = container_insulate - connectOUT_state * \
                                temperature + connectIN_state * fluidIN_temp
                    return temperature
            else:
                raise ValueError("Invalid type")

            contamination = State(
                name="contamination",
                value=0.,
            )

            @make_function(contamination)
            def calc_contamination(
                container_store=container_store,
                connectOUT_state=valveOUT_state,
                connectIN_state=valveIN_state,
                fluidIN_cont=fluidIN_cont,
                contamination=contamination
            ):
                contamination = (1 - container_store) - connectOUT_state *\
                                contamination + connectIN_state * fluidIN_cont
                return contamination

        else:

            volume = State(
                name="volume",
                value=1.,
            )

            @make_function(volume)
            def calc_volume(
                container_store=container_store,
                connectOUT_state=valveOUT_state,
                volume=volume
            ):
                volume = volume - (1 - container_store) - connectOUT_state * volume
                return volume

            pressure = State(
                name="pressure",
                value=1.0,
            )

            @make_function(pressure)
            def calc_pressure(
                container_store=container_store,
                connectOUT_state=valveOUT_state,
                pressure=pressure
            ):
                pressure = pressure - (1 - container_store) - connectOUT_state * pressure
                return pressure

            temperature = State(
                name="temperature",
                value=1.0,
            )

            if type == "heatIN":
                @make_function(temperature)
                def calc_temperature(
                    container_insulate=container_insulate,
                    connectOUT_state=valveOUT_state,
                    temperature=temperature,
                ):
                    temperature = temperature - container_insulate - connectOUT_state * \
                            temperature 
                    return temperature
            elif type == "heatOUT":
                @make_function(temperature)
                def calc_temperature(
                    container_insulate=container_insulate,
                    connectOUT_state=valveOUT_state,
                    temperature=temperature,
                    panel_loss=affect
                ):
                    temperature = temperature - panel_loss * container_insulate - connectOUT_state * \
                            temperature
                    return temperature
            elif type == "standard" or type == "pump":
                @make_function(temperature)
                def calc_temperature(
                    container_insulate=container_insulate,
                    connectOUT_state=valveOUT_state,
                    temperature=temperature,
                ):
                    temperature = temperature - (1 - container_insulate) - \
                            connectOUT_state * temperature
                    return temperature
            else:
                raise ValueError("Invalid type")

            contamination = State(
                name="contamination",
                value=0.,
            )

            @make_function(contamination)
            def calc_contamination(
                container_store=container_store,
                connectOUT_state=valveOUT_state,
                contamination=contamination
            ):
                contamination = contamination + (1 - container_store) - connectOUT_state *\
                                contamination
                return contamination

        coolant_functionality_inputs = (
            volume,
            pressure,
            temperature,
            contamination,
        )

        coolant_functionality = make_functionality(
            *coolant_functionality_inputs
        )

    return coolant

def make_pooled_coolant(
        name: str,
        plumbing1: System,
        plumbing2: System,
        plumbing3: Optional[System[None]]=None,
        plumbing4: Optional[System[None]]=None,
        plumbing5: Optional[System[None]]=None,
        plumbing6: Optional[System[None]]=None,
) -> System:

    with System(name=name) as pooled_coolant:

        volume = State(name="volume", value=1.0)
        pressure = State(name="pressure", value=1.0)
        temperature = State(name="temperature", value=1.0)
        contamination = State(name="contamination", value=0.0)

        if plumbing6 is not None:

            @make_function(volume)
            def calc_volume(
                v1 = plumbing1.coolant.volume,
                v1pos = plumbing1.valve.position,
                v2 = plumbing2.coolant.volume,
                v2pos = plumbing2.valve.position,
                v3 = plumbing3.coolant.volume,
                v3pos = plumbing3.valve.position,
                v4 = plumbing4.coolant.volume,
                v4pos = plumbing4.valve.position,
                v5 = plumbing5.coolant.volume,
                v5pos = plumbing5.valve.position,
                v6 = plumbing6.coolant.volume,
                v6pos = plumbing6.valve.position,
            ) -> float:
                volume = (v1*v1pos + v2*v2pos + v3*v3pos + v4*v4pos + v5*v5pos + v6*v6pos)/6
                return volume

            @make_function(pressure)
            def calc_pressure(
                p1 = plumbing1.coolant.pressure,
                v1pos = plumbing1.valve.position,
                p2 = plumbing2.coolant.pressure,
                v2pos = plumbing2.valve.position,
                p3 = plumbing3.coolant.pressure,
                v3pos = plumbing3.valve.position,
                p4 = plumbing4.coolant.pressure,
                v4pos = plumbing4.valve.position,
                p5 = plumbing5.coolant.pressure,
                v5pos = plumbing5.valve.position,
                p6 = plumbing6.coolant.pressure,
                v6pos = plumbing6.valve.position,
            ) -> float:
                pressure = (p1*v1pos + p2*v2pos + p3*v3pos + p4*v4pos + p5*v5pos + p6*v6pos)/6
                return pressure

            @make_function(temperature)
            def calc_temperature(
                t1 = plumbing1.coolant.temperature,
                t1pos = plumbing1.valve.position,
                t2 = plumbing2.coolant.temperature,
                t2pos = plumbing2.valve.position,
                t3 = plumbing3.coolant.temperature,
                t3pos = plumbing3.valve.position,
                t4 = plumbing4.coolant.temperature,
                t4pos = plumbing4.valve.position,
                t5 = plumbing5.coolant.temperature,
                t5pos = plumbing5.valve.position,
                t6 = plumbing6.coolant.temperature,
                t6pos = plumbing6.valve.position,
            ) -> float:
                temperature = (t1*t1pos + t2*t2pos + t3*t3pos + t4*t4pos + t5*t5pos + t6*t6pos)/6
                return temperature

            @make_function(contamination)
            def calc_contamination(
                c1 = plumbing1.coolant.contamination,
                c1pos = plumbing1.valve.position,
                c2 = plumbing2.coolant.contamination,
                c2pos = plumbing2.valve.position,
                c3 = plumbing3.coolant.contamination,
                c3pos = plumbing3.valve.position,
                c4 = plumbing4.coolant.contamination,
                c4pos = plumbing4.valve.position,
                c5 = plumbing5.coolant.contamination,
                c5pos = plumbing5.valve.position,
                c6 = plumbing6.coolant.contamination,
                c6pos = plumbing6.valve.position,
            ) -> float:
                contamination = (c1*c1pos + c2*c2pos + c3*c3pos + c4*c4pos + c5*c5pos + c6*c6pos)/6
                return contamination

        elif plumbing5 is not None:

            @make_function(volume)
            def calc_volume(
                v1 = plumbing1.coolant.volume,
                v1pos = plumbing1.valve.position,
                v2 = plumbing2.coolant.volume,
                v2pos = plumbing2.valve.position,
                v3 = plumbing3.coolant.volume,
                v3pos = plumbing3.valve.position,
                v4 = plumbing4.coolant.volume,
                v4pos = plumbing4.valve.position,
                v5 = plumbing5.coolant.volume,
                v5pos = plumbing5.valve.position,
            ) -> float:
                volume = (v1*v1pos + v2*v2pos + v3*v3pos + v4*v4pos + v5*v5pos)/5
                return volume

            @make_function(pressure)
            def calc_pressure(
                p1 = plumbing1.coolant.pressure,
                v1pos = plumbing1.valve.position,
                p2 = plumbing2.coolant.pressure,
                v2pos = plumbing2.valve.position,
                p3 = plumbing3.coolant.pressure,
                v3pos = plumbing3.valve.position,
                p4 = plumbing4.coolant.pressure,
                v4pos = plumbing4.valve.position,
                p5 = plumbing5.coolant.pressure,
                v5pos = plumbing5.valve.position,
            ) -> float:
                pressure = (p1*v1pos + p2*v2pos + p3*v3pos + p4*v4pos + p5*v5pos)/5
                return pressure

            @make_function(temperature)
            def calc_temperature(
                t1 = plumbing1.coolant.temperature,
                t1pos = plumbing1.valve.position,
                t2 = plumbing2.coolant.temperature,
                t2pos = plumbing2.valve.position,
                t3 = plumbing3.coolant.temperature,
                t3pos = plumbing3.valve.position,
                t4 = plumbing4.coolant.temperature,
                t4pos = plumbing4.valve.position,
                t5 = plumbing5.coolant.temperature,
                t5pos = plumbing5.valve.position,
            ) -> float:
                temperature = (t1*t1pos + t2*t2pos + t3*t3pos + t4*t4pos + t5*t5pos)/5
                return temperature

            @make_function(contamination)
            def calc_contamination(
                c1 = plumbing1.coolant.contamination,
                c1pos = plumbing1.valve.position,
                c2 = plumbing2.coolant.contamination,
                c2pos = plumbing2.valve.position,
                c3 = plumbing3.coolant.contamination,
                c3pos = plumbing3.valve.position,
                c4 = plumbing4.coolant.contamination,
                c4pos = plumbing4.valve.position,
                c5 = plumbing5.coolant.contamination,
                c5pos = plumbing5.valve.position,
            ) -> float:
                contamination = (c1*c1pos + c2*c2pos + c3*c3pos + c4*c4pos + c5*c5pos)/5
                return contamination

        elif plumbing4 is not None:

            @make_function(volume)
            def calc_volume(
                v1 = plumbing1.coolant.volume,
                v1pos = plumbing1.valve.position,
                v2 = plumbing2.coolant.volume,
                v2pos = plumbing2.valve.position,
                v3 = plumbing3.coolant.volume,
                v3pos = plumbing3.valve.position,
                v4 = plumbing4.coolant.volume,
                v4pos = plumbing4.valve.position,
            ) -> float:
                volume = (v1*v1pos + v2*v2pos + v3*v3pos + v4*v4pos)/4
                return volume

            @make_function(pressure)
            def calc_pressure(
                p1 = plumbing1.coolant.pressure,
                v1pos = plumbing1.valve.position,
                p2 = plumbing2.coolant.pressure,
                v2pos = plumbing2.valve.position,
                p3 = plumbing3.coolant.pressure,
                v3pos = plumbing3.valve.position,
                p4 = plumbing4.coolant.pressure,
                v4pos = plumbing4.valve.position,
            ) -> float:
                pressure = (p1*v1pos + p2*v2pos + p3*v3pos + p4*v4pos)/4
                return pressure

            @make_function(temperature)
            def calc_temperature(
                t1 = plumbing1.coolant.temperature,
                v1pos = plumbing1.valve.position,
                t2 = plumbing2.coolant.temperature,
                v2pos = plumbing2.valve.position,
                t3 = plumbing3.coolant.temperature,
                v3pos = plumbing3.valve.position,
                t4 = plumbing4.coolant.temperature,
                v4pos = plumbing4.valve.position,
            ) -> float:
                temperature = (t1*v1pos + t2*v2pos + t3*v3pos + t4*v4pos)/4
                return temperature

            @make_function(contamination)
            def calc_contamination(
                c1 = plumbing1.coolant.contamination,
                v1pos = plumbing1.valve.position,
                c2 = plumbing2.coolant.contamination,
                v2pos = plumbing2.valve.position,
                c3 = plumbing3.coolant.contamination,
                v3pos = plumbing3.valve.position,
                c4 = plumbing4.coolant.contamination,
                v4pos = plumbing4.valve.position,
            ) -> float:
                contamination = (c1*v1pos + c2*v2pos + c3*v3pos + c4*v4pos)/4
                return contamination

        elif plumbing3 is not None:

            @make_function(volume)
            def calc_volume(
                v1 = plumbing1.coolant.volume,
                v1pos = plumbing1.valve.position,
                v2 = plumbing2.coolant.volume,
                v2pos = plumbing2.valve.position,
                v3 = plumbing3.coolant.volume,
                v3pos = plumbing3.valve.position,
            ) -> float:
                volume = (v1*v1pos + v2*v2pos + v3*v3pos)/3
                return volume

            @make_function(pressure)
            def calc_pressure(
                p1 = plumbing1.coolant.pressure,
                v1pos = plumbing1.valve.position,
                p2 = plumbing2.coolant.pressure,
                v2pos = plumbing2.valve.position,
                p3 = plumbing3.coolant.pressure,
                v3pos = plumbing3.valve.position,
            ) -> float:
                pressure = (p1*v1pos + p2*v2pos + p3*v3pos)/3
                return pressure

            @make_function(temperature)
            def calc_temperature(
                t1 = plumbing1.coolant.temperature,
                v1pos = plumbing1.valve.position,
                t2 = plumbing2.coolant.temperature,
                v2pos = plumbing2.valve.position,
                t3 = plumbing3.coolant.temperature,
                v3pos = plumbing3.valve.position,
            ) -> float:
                temperature = (t1*v1pos + t2*v2pos + t3*v3pos)/3
                return temperature

            @make_function(contamination)
            def calc_contamination(
                c1 = plumbing1.coolant.contamination,
                v1pos = plumbing1.valve.position,
                c2 = plumbing2.coolant.contamination,
                v2pos = plumbing2.valve.position,
                c3 = plumbing3.coolant.contamination,
                v3pos = plumbing3.valve.position,
            ) -> float:
                contamination = (c1*v1pos + c2*v2pos + c3*v3pos)/3
                return contamination

        else: 

            @make_function(volume)
            def calc_volume(
                v1 = plumbing1.coolant.volume,
                v1pos = plumbing1.valve.position,
                v2 = plumbing2.coolant.volume,
                v2pos = plumbing2.valve.position,
            ) -> float:
                volume = (v1*v1pos + v2*v2pos)/2
                return volume

            @make_function(pressure)
            def calc_pressure(
                p1 = plumbing1.coolant.pressure,
                v1pos = plumbing1.valve.position,
                p2 = plumbing2.coolant.pressure,
                v2pos = plumbing2.valve.position,
            ) -> float:
                pressure = (p1*v1pos + p2*v2pos)/2
                return pressure

            @make_function(temperature)
            def calc_temperature(
                t1 = plumbing1.coolant.temperature,
                v1pos = plumbing1.valve.position,
                t2 = plumbing2.coolant.temperature,
                v2pos = plumbing2.valve.position,
            ) -> float:
                temperature = (t1*v1pos + t2*v2pos)/2
                return temperature

            @make_function(contamination)
            def calc_contamination(
                c1 = plumbing1.coolant.contamination,
                v1pos = plumbing1.valve.position,
                c2 = plumbing2.coolant.contamination,
                v2pos = plumbing2.valve.position,
            ) -> float:
                contamination = (c1*v1pos + c2*v2pos)/2
                return contamination

    return pooled_coolant
