from cdcm import * 
from cdcm_abstractions import *

import numpy as np 

__all__ = ["get_surface"]

def get_surface(
    name: str,
    clock: system, 
    sun: Variable,
    shift: float 
) -> System: 
    
    with System (name=name) as surface: 
        
        temperature = Variable(name="temperature", value=0.0)
        drift = Parameter(name="drift", value=shift)

        @make_function(temperature) 
        def calc_temperature(
            s=sun,
            t=clock.t,
            d=drift
        ): 
            if s > 0: 
                return (-1368*np.sin(2*np.pi*t/(708) + d))/11.35
            else: 
                return (-1368*np.sin(2*np.pi*t/(708) + d))/10.45 
        
    return surface