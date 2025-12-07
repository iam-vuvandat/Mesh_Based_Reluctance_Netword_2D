import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  

from motor_geometry.models.SPM import SPM
spm = SPM()

from motor_geometry.utils.create_adaptive_trapezoid_grid_for_SPM import create_adaptive_trapezoid_grid_for_SPM
grid = create_adaptive_trapezoid_grid_for_SPM(spm,1,1,3,3,3,1,90)

from motor_geometry.core.extract_motor_segment import extract_motor_segment
segment = extract_motor_segment(spm,0,0)

from motor_geometry.models.ReluctanceNetwork import ReluctanceNetwork
reluctance_network = ReluctanceNetwork(segments= segment, grid= grid)
reluctance_network.display()