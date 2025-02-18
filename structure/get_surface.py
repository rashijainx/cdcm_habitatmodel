from cdcm import * 
from cdcm_abstractions import *

__all__ = ["get_surface"]

def get_surface(
    name: str,
    irradiance: Variable,
    albedo: Variable, 
) -> System: 
    
    with System (name=name) as surface: 
        
        temperature = Variable(name="temperature", value=0.0)

        sigma = Parameter(name="sigma", value=5.67e-8)

        @make_function(temperature)
        def calc_temperature(
            S=irradiance,
            sigma=sigma,
            albedo=albedo
        ):
            return ((1 - albedo)*S/sigma)**0.25 - 273.15
        
    return surface