import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  

from motor_geometry.models.SPM import SPM
spm = SPM(magnet_arc = 125)
spm.solve_open_circuit(show_plot=True)