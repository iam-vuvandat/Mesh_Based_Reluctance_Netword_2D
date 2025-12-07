import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) 

import math 
from motor_geometry.models.SPM import SPM 
from motor_geometry.utils.create_trapezoid_grid import create_trapezoid_grid
from motor_geometry.models.ReluctanceNetwork import ReluctanceNetwork
from motor_geometry.utils.create_adaptive_trapezoid_grid_for_SPM import create_adaptive_trapezoid_grid_for_SPM
from motor_geometry.utils.create_cartesian_grid import create_cartesian_grid
pi = math.pi 

spm = SPM()
segments = spm.extract_segments(stator_angle_offset=-6 * 180/ pi  )
grid3 = create_adaptive_trapezoid_grid_for_SPM(spm,3,3,5,6,5,3,180)
reluctance_network4 = ReluctanceNetwork(segments=segments,grid=grid3)
reluctance_network4.display()

grid = create_trapezoid_grid(second_dimension_begin=10,
                             second_dimension_end=11,
                             npoint_second_dimension=3,
                             first_dimension_begin=70 * pi / 180,
                             first_dimension_end=110 * pi / 180,
                             npoint_first_dimension= 30)
grid.display(linewidth=1.0, alpha=1.0,three_dimension= True, z_height= 5,linewidth_top=0.5,linewidth_vertical= 0.0)









grid = create_adaptive_trapezoid_grid_for_SPM(spm,2,5,5,12,12,1,210,theta_begin = 0, theta_end = pi / 2)
reluctance_network = ReluctanceNetwork(segments=segments,grid=grid)
reluctance_network.display()

"""

grid1 = create_cartesian_grid(first_dimension_begin=0,
                              first_dimension_end=0.1,
                              npoint_first_dimension=200,
                              second_dimension_begin=0,
                              second_dimension_end=0.1,
                              npoint_second_dimension=200)
reluctance_network1 = ReluctanceNetwork(segments=segments,grid=grid1)
reluctance_network1.display()
"""

