import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) 

from motor_geometry.utils.create_trapezoid_grid import create_trapezoid_grid
import math 
pi = math.pi 

r_begin         = 14
r_end           = 22
n_point_r       = 4
theta_begin     = ( 90 - 40 ) * pi / 180 
theta_end       = ( 90 + 40 ) * pi / 180 
n_point_theta   = 6

grid = create_trapezoid_grid(theta_begin,theta_end,n_point_theta,r_begin,r_end,n_point_r)
grid.display(linewidth = 1.0, alpha = 1.0,three_dimension=True, z_height=20)

