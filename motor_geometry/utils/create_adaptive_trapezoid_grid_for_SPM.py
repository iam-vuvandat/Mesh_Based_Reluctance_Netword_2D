import math
import numpy as np
from motor_geometry.models.Grid import Grid

def create_adaptive_trapezoid_grid_for_SPM(motor_input, n_1, n_2, n_3, n_4, n_5, n_6, n_theta,reduce = "reduce",theta_begin = None, theta_end = None):
    
    """
    Tạo lưới cực thích ứng cho loại động cơ SPM
    Bán kính không đều
    Bước góc theta đều
    """

    # Trích xuất geometry và vật liệu 
    Dir             = motor_input.shaft_diameter
    pole_pair       = motor_input.pole_pair_number
    p               = motor_input.pole_number
    Dis             = motor_input.stator_bore_diameter
    g               = motor_input.air_gap
    hm              = motor_input.magnet_thickness
    mArc            = motor_input.magnet_arc
    Dos             = motor_input.stator_lamination_outer_diameter
    Qs              = motor_input.slot_number 
    bs0             = motor_input.slot_opening
    hs0             = motor_input.tooth_tip_depth
    wt              = motor_input.tooth_width
    tooth_tip_angle = motor_input.tooth_tip_angle
    hs              = motor_input.slot_depth
    length          = motor_input.motor_axial_length 
    Qs_reduced      = motor_input.slot_number_reduced
    p_pair_reduced  = motor_input.pole_pair_number_reduced

    pi = math.pi

    # ===== Rotor yoke =====
    r_shaft = Dir / 2
    r_rotor_yoke = Dis / 2 - g - hm
    r_1 = np.linspace(r_shaft, r_rotor_yoke, n_1 + 1)
    r_0 = np.linspace(r_shaft * 0.998, r_shaft, 2) # lớp đệm bên trong
    # lớp đệm bên trong
    #r_0 = np.linspace(r_shaft* 0.95, r_shaft,2)

    # ===== Magnet =====
    r_magnet = r_rotor_yoke + hm
    r_2 = np.linspace(r_rotor_yoke, r_magnet, n_2 + 1)

    # ===== Airgap =====
    r_airgap = Dis / 2
    r_3 = np.linspace(r_magnet, r_airgap, n_3 + 1)

    # ===== Tooth tip =====
    r_in_tooth_tip = Dis / 2
    C_in_stator = r_in_tooth_tip * 2 * pi
    r_out_tooth_tip = r_in_tooth_tip + hs0 + (
        ((C_in_stator / Qs) - bs0 - wt) / 2
    ) * np.tan(tooth_tip_angle * pi / 180)
    r_4 = np.linspace(r_airgap, r_out_tooth_tip, n_4 + 1)

    # ===== Tooth body =====
    r_stator_yoke = r_out_tooth_tip + hs
    r_5 = np.linspace(r_out_tooth_tip, r_stator_yoke, n_5 + 1)

    # ===== Stator yoke =====
    r_6 = np.linspace(r_stator_yoke, Dos / 2, n_6 + 1)
    r_7 = np.linspace(Dos/2,(Dos/2)*1.00001,2)

    # ===== Gộp lại =====
    r = np.concatenate([r_0, r_1[1:], r_2[1:], r_3[1:], 
                    r_4[1:], r_5[1:], r_6[1:],r_7[1:]])
    if theta_begin == None or theta_end == None:
        if reduce =="reduce":
            # ===== Chia theo góc =====
            k = Qs / Qs_reduced
            theta = np.linspace(2 * pi / k, 0 , n_theta)
        elif reduce =="no_reduce":
            theta = np.linspace(2*pi,0, n_theta)
    
    else:
        theta = np.linspace(theta_begin,theta_end,n_theta)
        
    polar_coords = [theta,r]
    return Grid(polar_coords,"trapezoid")
