import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  

import math
pi= math.pi
from motor_geometry.models.SPM import SPM
spm = SPM()

from motor_geometry.core.extract_motor_segment import extract_motor_segment
offset_stator = -6* pi / 180
offset_rotor  = 0 * pi / 180
segments = extract_motor_segment(spm,rotor_angle_offset= offset_rotor, stator_angle_offset= offset_stator)
from motor_geometry.utils.create_adaptive_trapezoid_grid_for_SPM import create_adaptive_trapezoid_grid_for_SPM
grid = create_adaptive_trapezoid_grid_for_SPM(spm,10,10,10,10,10,10,180)

from motor_geometry.models.ReluctanceNetwork import ReluctanceNetwork
reluctance_network = ReluctanceNetwork(segments=segments,
                                       grid=grid,
                                       optimization="vectorized",
                                       cyclic_type = "first_dimension")
#reluctance_network.display()
from solver.core.fixed_point_iteration import fixed_point_iteration
reluctance_network = fixed_point_iteration(reluctance_network=reluctance_network,detail_debug = True)
reluctance_network.view_flux_density(show_plot = True,show_full = False)

flux_density =  reluctance_network.export_flux_density(position = 5)

import matplotlib.pyplot as plt
x = flux_density[-1]
y_data = flux_density[:-1]

plt.figure(figsize=(8, 4))
for i, y in enumerate(y_data, start=1):
    plt.plot(x, y, label=f"Thành phần {i}")

plt.xlabel("Trục x (hàng cuối)")
plt.ylabel("Mật độ từ thông (T)")
plt.title("Biểu đồ mật độ từ thông theo vị trí")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

