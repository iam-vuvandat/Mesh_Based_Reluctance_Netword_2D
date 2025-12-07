import numpy as np
import math
from motor_geometry.utils.create_arc import create_arc
from motor_geometry.utils.create_line import create_line
from motor_geometry.utils.create_line_from_points import create_line_from_points
from motor_geometry.utils.create_point import create_point
from motor_geometry.utils.rotate_line import rotate_line
from motor_geometry.utils.rotate_point import rotate_point
from motor_geometry.utils.rotate_segment import rotate_segment
from motor_geometry.utils.get_begin_point import get_begin_point
from motor_geometry.utils.get_end_point import get_end_point
from motor_geometry.utils.create_polygon import create_polygon
from solver.utils.create_column_array import create_column_array
from motor_geometry.models.Segment import Segment
from shapely.geometry import Point
pi = math.pi

def extract_motor_segment(motor_input,rotor_angle_offset,stator_angle_offset):
    """
    Tạo tập hợp các segment từ geometry động cơ và các đầu vào, bao gồm kích thích stator
    """
    # Tạo mảng rỗng chứa các segments
    segments=[]
    
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
    phase_number    = motor_input.phase_number
    H0              = motor_input.material_database.magnet.coercivity

    # Lực từ động nam châm vĩnh cửu 
    F_m = H0*hm
    # Tạo mảng không có kích thích stator
    no_stator_excitation = create_column_array([],phase_number)
    # Template rotor_yoke 
        # Rotor yoke
    r_yoke_in = Dir / 2
    r_yoke_out = Dis / 2 - g - hm
    arc_pole = 2 * pi / p

    stator_angle_offset = -(stator_angle_offset + arc_pole/2)

    rotor_yoke_in_line = create_arc(r_yoke_in, 0, arc_pole)
    rotor_yoke_out_line = create_arc(r_yoke_out, 0, arc_pole)
    rotor_yoke_line_left = create_line_from_points(get_begin_point(rotor_yoke_in_line),
                                                   get_begin_point(rotor_yoke_out_line))
    rotor_yoke_line_right = create_line_from_points(get_end_point(rotor_yoke_in_line),
                                                    get_end_point(rotor_yoke_out_line))
    rotor_yoke = create_polygon(rotor_yoke_in_line, rotor_yoke_out_line,
                                rotor_yoke_line_left, rotor_yoke_line_right)
    rotor_yoke=Segment(rotor_yoke,"iron",0,length,0,0,no_stator_excitation,0)

    # =====================
    # Rotor magnet
    arc_magnet = arc_pole * mArc / 180
    arc_magnet1 = (arc_pole - arc_magnet) / 2
    arc_magnet2 = arc_magnet1 + arc_magnet
    magnet_in_line = create_arc(r_yoke_out, arc_magnet1, arc_magnet2)
    magnet_out_line = create_arc(r_yoke_out + hm, arc_magnet1, arc_magnet2)
    magnet_line_left = create_line_from_points(get_begin_point(magnet_in_line),
                                               get_begin_point(magnet_out_line))
    magnet_line_right = create_line_from_points(get_end_point(magnet_in_line),
                                                get_end_point(magnet_out_line))
    rotor_magnet = create_polygon(magnet_in_line, magnet_out_line,
                                  magnet_line_left, magnet_line_right)
    magnet=Segment(rotor_magnet, "magnet",0,length,F_m,0,no_stator_excitation,0)

    # =================
    # Tooth tip
    r_tooth_tip = Dis / 2
    C_in_stator = Dis * pi
    C_slot = C_in_stator / Qs
    C_tooth_tip = C_slot - bs0
    arc_tooth_tip = 2 * pi * C_tooth_tip / C_in_stator
    arc_slot = 2 * pi * C_slot / C_in_stator
    arc_tooth_tip1 = (arc_slot - arc_tooth_tip) / 2
    arc_tooth_tip2 = arc_tooth_tip1 + arc_tooth_tip

    tooth_tip_out = create_arc(r_tooth_tip, arc_tooth_tip1, arc_tooth_tip2)
    tooth_tip_dot1 = get_end_point(tooth_tip_out)
    tooth_tip_depth = r_tooth_tip + hs0
    tooth_tip_depth_dot1 = rotate_point(Point(tooth_tip_depth, 0), arc_tooth_tip2)
    tooth_tip_left = create_line_from_points(tooth_tip_dot1, tooth_tip_depth_dot1)

    tooth_tip_dot2 = get_begin_point(tooth_tip_out)
    tooth_tip_depth_dot2 = rotate_point(Point(tooth_tip_depth, 0), arc_tooth_tip1)
    tooth_tip_right = create_line_from_points(tooth_tip_dot2, tooth_tip_depth_dot2)

    r_tooth_tip_in = r_tooth_tip + hs0 + (((C_in_stator / Qs) - bs0 - wt) / 2) * np.tan(tooth_tip_angle * pi / 180)
    arc_in_tooth_tip = 2 * np.arctan((wt / 2) / r_tooth_tip_in)
    arc_in_tooth_tip1 = 0.5 * (arc_slot - arc_in_tooth_tip)
    arc_in_tooth_tip2 = arc_in_tooth_tip1 + arc_in_tooth_tip

    dot_tooth_tip_in1 = rotate_point(Point(r_tooth_tip_in, 0), arc_in_tooth_tip2)
    tooth_tip_left2 = create_line_from_points(tooth_tip_depth_dot1, dot_tooth_tip_in1)
    dot_tooth_tip_in2 = rotate_point(Point(r_tooth_tip_in, 0), arc_in_tooth_tip1)
    tooth_tip_right2 = create_line_from_points(tooth_tip_depth_dot2, dot_tooth_tip_in2)
    tooth_tip_in = create_line_from_points(dot_tooth_tip_in1, dot_tooth_tip_in2)

    tooth_tip = create_polygon(tooth_tip_out,
                                     tooth_tip_left,
                                     tooth_tip_right,
                                     tooth_tip_left2,
                                     tooth_tip_right2,
                                     tooth_tip_in)
    tooth_tip=Segment(tooth_tip, "iron",0,length,0,0,no_stator_excitation,0)

    # =================
    # Tooth
    r_stator_yoke = r_tooth_tip_in + hs
    arc_open_tooth_in = 2 * np.atan((wt / 2) / r_stator_yoke)
    arc_tooth_in1 = (arc_slot / 2) - (0.5 * arc_open_tooth_in)
    arc_tooth_in2 = (arc_slot / 2) + (0.5 * arc_open_tooth_in)

    dot_tooth_in = Point(r_stator_yoke, 0)
    dot_tooth_in1 = rotate_point(dot_tooth_in, arc_tooth_in1)
    dot_tooth_in2 = rotate_point(dot_tooth_in, arc_tooth_in2)

    dot_tooth_out = Point(r_tooth_tip_in, 0)
    dot_tooth_out1 = rotate_point(dot_tooth_out, arc_in_tooth_tip1)
    dot_tooth_out2 = rotate_point(dot_tooth_out, arc_in_tooth_tip2)

    tooth_line_right = create_line_from_points(dot_tooth_in1, dot_tooth_out1)
    tooth_line_left = create_line_from_points(dot_tooth_in2, dot_tooth_out2)
    tooth_line_in = create_line_from_points(dot_tooth_in1, dot_tooth_in2)
    tooth_line_out = tooth_tip_in

    tooth = create_polygon(tooth_line_left, tooth_line_right, tooth_line_in, tooth_line_out)
    tooth=Segment(tooth, "iron",0,length,0,0,motor_input.stator_excitation_coeffs[0],0)

    # Stator yoke
    r_out_stator_yoke = Dos / 2
    stator_yoke_line1 = create_arc(r_stator_yoke, 0, arc_tooth_in1)
    stator_yoke_line2 = create_arc(r_stator_yoke, arc_tooth_in2, arc_slot)
    stator_yoke_out_line = create_arc(r_out_stator_yoke, 0, arc_slot)

    dot_stator_yoke_right_out = get_begin_point(stator_yoke_out_line)
    dot_stator_yoke_left_out = get_end_point(stator_yoke_out_line)
    dot_stator_yoke_right_in = get_begin_point(stator_yoke_line1)
    dot_stator_yoke_left_in = get_end_point(stator_yoke_line2)

    stator_yoke_line_right = create_line_from_points(dot_stator_yoke_right_out, dot_stator_yoke_right_in)
    stator_yoke_line_left = create_line_from_points(dot_stator_yoke_left_out, dot_stator_yoke_left_in)

    stator_yoke = create_polygon(stator_yoke_line1, stator_yoke_line2,
                                 stator_yoke_line_right, stator_yoke_line_left,
                                 stator_yoke_out_line, tooth_line_in)
    stator_yoke=Segment(stator_yoke, "iron",0,length,0,0,no_stator_excitation,0)

    # Nhân bản 
    #nhân bản rotor yoke    
    for i in range(p):
        theta_rotate = rotor_angle_offset + i* arc_pole
        copy_of_rotor_yoke=rotate_segment(rotor_yoke,-theta_rotate)
        segments.append(copy_of_rotor_yoke)
        segments[-1].index = i

    # nhân bản nam châm và gán cực xen kẽ 
    for i in range(p):
        theta_rotate = rotor_angle_offset + i* arc_pole
        copy_of_magnet=rotate_segment(magnet,-theta_rotate)
        segments.append(copy_of_magnet)
        segments[-1].index = i
        if i % 2 ==0:
            segments[-1].delta_angle_magnetic_source = 0
        else:
            segments[-1].delta_angle_magnetic_source = -pi

    # nhân bản tooth tip 
    
    for i in range(Qs):
        theta_rotate = stator_angle_offset + i * arc_slot
        copy_of_tooth_tip=rotate_segment(tooth_tip,-theta_rotate)
        segments.append(copy_of_tooth_tip)
        segments[-1].index = i

    # nhân bản răng 
    for i in range(Qs):
        theta_rotate = stator_angle_offset + i * arc_slot
        copy_of_tooth=rotate_segment(tooth,-theta_rotate)
        segments.append(copy_of_tooth)
        segments[-1].index = i
        segments[-1].stator_excitation_coeffs=motor_input.stator_excitation_coeffs[i]

    # nhân bản stator yoke 
    for i in range(Qs):
        theta_rotate = stator_angle_offset + i * arc_slot
        copy_of_stator_yoke=rotate_segment(stator_yoke,-theta_rotate)
        segments.append(copy_of_stator_yoke)
        segments[-1].index = i
    
    return segments