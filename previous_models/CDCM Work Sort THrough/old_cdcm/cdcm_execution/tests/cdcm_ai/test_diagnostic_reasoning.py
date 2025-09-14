#~ovn!
"""Test meta-programs that perform diagnostic reasoning

Author:
    R Murali Krishnan
    
Date:
    04.06.2023
    
"""


from cdcm import *
from cdcm_abstractions import *
from cdcm_mcvt import *
from cdcm_ai import *

from pprint import pprint


with System(name="hab") as hab:
    
    clock = make_clock(dt=1, units="hr")

    power_system = make_power_system("power")




print("~ovn!")
dreasoner = DiagnosticReasoner(hab)
print(dreasoner)
print(dreasoner.process())