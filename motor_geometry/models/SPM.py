import numpy as np
from material_data.models.MaterialDataBase import MaterialDataBase
from motor_geometry.utils.simplify_fraction import simplify_fraction
from solver.utils.create_column_array import create_column_array
from motor_geometry.utils.cogging_period_angle import cogging_period_angle
from solver.core.solver_open_circuit_for_spm import solve
from data.utils.data_helper import save
from solver.utils.create_high_resolution_gif_for_spm import create_gif
import math

from motor_geometry.core.extract_motor_segment import extract_motor_segment
pi = math.pi

class SPM:
    def __init__(self,
                 name = 0,
                 # Stator parameters
                 slot_number=15,
                 stator_lamination_outer_diameter=196e-3,
                 stator_bore_diameter=120e-3,
                 tooth_width=15e-3,
                 slot_depth=25e-3,
                 slot_corner_radius=0,
                 tooth_tip_depth=1e-3,
                 slot_opening=5e-3,
                 tooth_tip_angle=30,
                 sleeve_thickness=0,
                 
                 # Rotor parameters
                 pole_number=10,
                 magnet_thickness=3e-3,
                 magnet_reduction=0,
                 magnet_arc=120,
                 magnet_segment=1,
                 air_gap=1.5e-3,
                 banding_thickness=0,
                 shaft_diameter=96e-3,
                 shaft_hole_diameter=0,
                 
                 # Motor length
                 motor_axial_length=120e-3,
                 
                 # Winding
                 number_of_turns_per_coil=25,
                 winding_type="concentrated",
                 phase_number=3,
                 shaft_speed = 1500 # rpm
                 ):

        # Tên động cơ
        self.name = name

        # --- Stator ---
        self.slot_number = slot_number
        self.stator_lamination_outer_diameter = stator_lamination_outer_diameter
        self.stator_bore_diameter = stator_bore_diameter
        self.tooth_width = tooth_width
        self.slot_depth = slot_depth
        self.slot_corner_radius = slot_corner_radius
        self.tooth_tip_depth = tooth_tip_depth
        self.slot_opening = slot_opening
        self.tooth_tip_angle = tooth_tip_angle
        self.sleeve_thickness = sleeve_thickness

        # --- Rotor ---
        self.pole_number = pole_number
        self.pole_pair_number = self.pole_number // 2
        self.magnet_thickness = magnet_thickness
        self.magnet_reduction = magnet_reduction
        self.magnet_arc = magnet_arc
        self.magnet_segment = magnet_segment
        self.air_gap = air_gap
        self.banding_thickness = banding_thickness
        self.shaft_diameter = shaft_diameter
        self.shaft_hole_diameter = shaft_hole_diameter

        # --- Length ---
        self.motor_axial_length = motor_axial_length

        # --- Winding ---
        self.number_of_turns_per_coil = number_of_turns_per_coil
        self.winding_type = winding_type
        self.phase_number = phase_number

        #shaft 
        self.shaft_speed = shaft_speed

        # --- Slot/pole fraction rút gọn ---
        self.slot_number_reduced, self.pole_pair_number_reduced = simplify_fraction(self.slot_number, self.pole_pair_number)
        self.pole_number_reduced = 2 * self.pole_pair_number_reduced
        self.reduce_factor = self.slot_number / self.slot_number_reduced
        self.theta_reduced = 2 * pi / self.reduce_factor

        # --- Material database ---
        self.material_database = MaterialDataBase()

        # --- Stator excitation coefficients ---
        self.stator_excitation_coeffs = self.generate_stator_excitation_coeffs(self.winding_type, self.phase_number)

        # --- Cogging torque period angle (rad) ---
        self.cogging_period_angle = cogging_period_angle(self.slot_number, self.pole_number)

        self.open_circuit_data = []
        

    def generate_stator_excitation_coeffs(self, winding_type="concentrated", phase_number=3):
        N = self.number_of_turns_per_coil
        coeffs = []
        if winding_type == "concentrated":
            base = [0] * phase_number
            for i in range(self.slot_number):
                phase_idx = i % phase_number
                col = base.copy()
                col[phase_idx] = N
                
                # === DÒNG CODE ĐÃ SỬA ===
                # Bỏ dấu * và dùng tên hàm mới
                coeffs.append(create_column_array(elements_list=col))
                # =========================
                
        return coeffs

    def solve_open_circuit(self,
                           solve_airgap=True,
                           solve_flux_linkage=True,
                           solve_back_emf_phase=True,
                           solve_back_emf_line=True,
                           solve_cogging_torque=True,
                           show_plot=True,
                           debug=False,
                           save_data = True,
                           quality = "medium",
                           angle_unit = "degree"):
        return solve(self,
                    solve_airgap,
                    solve_flux_linkage,
                    solve_back_emf_phase,
                    solve_back_emf_line,
                    solve_cogging_torque,
                    show_plot,
                    debug,
                    save_data,
                    quality,
                    angle_unit
                    )
        
    def create_gif(self,path=None, show_plot=True, debug=False):
        create_gif(self, path=path, show_plot=show_plot, debug=debug)

    def extract_segments(self,stator_angle_offset = 0, rotor_angle_offset = 0 ):
        return extract_motor_segment(motor_input= self, stator_angle_offset= stator_angle_offset,rotor_angle_offset = rotor_angle_offset)

        
