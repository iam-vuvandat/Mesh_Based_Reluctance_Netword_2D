import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))  

from ansys.utils.load_motor_cad import load_motor_cad
from system.utils.find_locate import find_locate

mcad = load_motor_cad(find_locate("data","model","5.mot"))     


