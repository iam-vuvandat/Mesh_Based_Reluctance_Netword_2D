import sys, os
from motor_geometry.core.extract_motor_segment import extract_motor_segment
from motor_geometry.utils.display_segments import display_segments
from motor_geometry.utils.create_adaptive_trapezoid_grid_for_SPM import create_adaptive_trapezoid_grid_for_SPM
from motor_geometry.models.ReluctanceNetwork import ReluctanceNetwork
from solver.core.fixed_point_iteration import fixed_point_iteration
from solver.utils.find_solver_parameter import find_solver_parameter
from solver.utils.periodic_derivative import periodic_derivative
from solver.utils.duplicate_periodic_data import duplicate_periodic_data
from solver.core.quasi_newton import quasi_newton
from tqdm import tqdm 
import matplotlib.pyplot as plt
import numpy as np
import math
import time
from system.utils.print_inline import print_inline
pi = math.pi
TQDM_KWARGS = dict(bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}", ncols=70, ascii=False, colour="red", leave=False)



def solve(spm, solve_airgap=True, solve_flux_linkage=True, solve_back_emf_phase=True, solve_back_emf_line=True, solve_cogging_torque=True, show_plot=True, debug=False, save_data=True, quality="medium", angle_unit="radian"):
    plot_data = []
    segments = extract_motor_segment(spm, 0, 0)
    if debug: display_segments(segments)
    n_rotor_yoke, n_magnet, n_airgap, n_tooth_tip, n_tooth, n_stator_yoke = [0]*6
    total_col, theta_resolution, step_cogging, step_standard, n_point_cogging, n_point_standard, n_point_check = [0]*7
    grid = None
    if quality == "low":
        total_col, theta_resolution, step_cogging, step_standard, n_point_cogging, n_point_standard, n_point_check = find_solver_parameter(spm,n_point_plot=17)
        n_rotor_yoke, n_magnet, n_airgap, n_tooth_tip, n_tooth, n_stator_yoke = 1,1,5,3,2,1
    elif quality == "medium":
        total_col, theta_resolution, step_cogging, step_standard, n_point_cogging, n_point_standard, n_point_check = find_solver_parameter(spm,n_point_plot=33)
        n_rotor_yoke, n_magnet, n_airgap, n_tooth_tip, n_tooth, n_stator_yoke = 6,6,5,6,6,6
        #total_col, theta_resolution, step_cogging, step_standard, n_point_cogging, n_point_standard, n_point_check = find_solver_parameter(spm,n_point_plot=33)
        #n_rotor_yoke, n_magnet, n_airgap, n_tooth_tip, n_tooth, n_stator_yoke = 2,2,5,4,3,2
    elif quality == "high":
        total_col, theta_resolution, step_cogging, step_standard, n_point_cogging, n_point_standard, n_point_check = find_solver_parameter(spm,n_point_plot=33)
        n_rotor_yoke, n_magnet, n_airgap, n_tooth_tip, n_tooth, n_stator_yoke = 4,6,10,8,6,4
    elif quality == "extreme":
        total_col, theta_resolution, step_cogging, step_standard, n_point_cogging, n_point_standard, n_point_check = find_solver_parameter(spm,n_point_plot=33)
        n_rotor_yoke, n_magnet, n_airgap, n_tooth_tip, n_tooth, n_stator_yoke = 6,6,12,12,6,6
    # Nếu truyền vào số
    elif quality == 0:
        total_col, theta_resolution, step_cogging, step_standard, n_point_cogging, n_point_standard, n_point_check = find_solver_parameter(spm,n_point_plot=33)
        n_rotor_yoke, n_magnet, n_airgap, n_tooth_tip, n_tooth, n_stator_yoke = 1,1,3,2,1,1
    elif quality == 1:
        total_col, theta_resolution, step_cogging, step_standard, n_point_cogging, n_point_standard, n_point_check = find_solver_parameter(spm,n_point_plot=33)
        n_rotor_yoke, n_magnet, n_airgap, n_tooth_tip, n_tooth, n_stator_yoke = 1,1,5,3,1,1
    elif quality == 2:
        total_col, theta_resolution, step_cogging, step_standard, n_point_cogging, n_point_standard, n_point_check = find_solver_parameter(spm,n_point_plot=33)
        n_rotor_yoke, n_magnet, n_airgap, n_tooth_tip, n_tooth, n_stator_yoke = 2,1,5,3,2,1
    elif quality == 3:
        total_col, theta_resolution, step_cogging, step_standard, n_point_cogging, n_point_standard, n_point_check = find_solver_parameter(spm,n_point_plot=33)
        n_rotor_yoke, n_magnet, n_airgap, n_tooth_tip, n_tooth, n_stator_yoke = 2,2,5,3,2,2
    elif quality == 4:
        total_col, theta_resolution, step_cogging, step_standard, n_point_cogging, n_point_standard, n_point_check = find_solver_parameter(spm,n_point_plot=33)
        n_rotor_yoke, n_magnet, n_airgap, n_tooth_tip, n_tooth, n_stator_yoke = 2,2,5,4,3,2
    elif quality == 5:
        total_col, theta_resolution, step_cogging, step_standard, n_point_cogging, n_point_standard, n_point_check = find_solver_parameter(spm,n_point_plot=33)
        n_rotor_yoke, n_magnet, n_airgap, n_tooth_tip, n_tooth, n_stator_yoke = 2,3,5,4,4,2
    elif quality == 6:
        total_col, theta_resolution, step_cogging, step_standard, n_point_cogging, n_point_standard, n_point_check = find_solver_parameter(spm,n_point_plot=33)
        n_rotor_yoke, n_magnet, n_airgap, n_tooth_tip, n_tooth, n_stator_yoke = 3,4,5,5,5,3
    elif quality == 7:
        total_col, theta_resolution, step_cogging, step_standard, n_point_cogging, n_point_standard, n_point_check = find_solver_parameter(spm,n_point_plot=33)
        n_rotor_yoke, n_magnet, n_airgap, n_tooth_tip, n_tooth, n_stator_yoke = 6,6,5,6,6,6
    elif quality == 8:
        total_col, theta_resolution, step_cogging, step_standard, n_point_cogging, n_point_standard, n_point_check = find_solver_parameter(spm,n_point_plot=33)
        n_rotor_yoke, n_magnet, n_airgap, n_tooth_tip, n_tooth, n_stator_yoke = 6,7,7,7,7,7
    elif quality == 9:
        total_col, theta_resolution, step_cogging, step_standard, n_point_cogging, n_point_standard, n_point_check = find_solver_parameter(spm,n_point_plot=33)
        n_rotor_yoke, n_magnet, n_airgap, n_tooth_tip, n_tooth, n_stator_yoke = 8,8,8,8,8,8
        

    else: # Trường hợp truyền vào số cột
        total_col, theta_resolution, step_cogging, step_standard, n_point_cogging, n_point_standard, n_point_check = find_solver_parameter(spm,n_point_plot=33)
        n_rotor_yoke, n_magnet, n_airgap, n_tooth_tip, n_tooth, n_stator_yoke = 1+quality,1+quality,5+quality,3+quality,1+quality,1+quality
    
    
    
    n_theta = total_col
    grid = create_adaptive_trapezoid_grid_for_SPM(spm,n_rotor_yoke,n_magnet,n_airgap,n_tooth_tip,n_tooth,n_stator_yoke,n_theta+1)
    reluctance_network = ReluctanceNetwork(segments, grid, cyclic_type="first_dimension")
    if debug:
        reluctance_network.display()
        matrix_size = reluctance_network.loop_flux_array.data.size
        print("Matrix size:",matrix_size,"x",matrix_size)
    number_of_rows, number_of_cols = reluctance_network.size
    ring_shift = (n_rotor_yoke+1, n_rotor_yoke+n_magnet)
    airgap_position = int(n_rotor_yoke + n_magnet + n_airgap // 2)+1
    delta_theta = reluctance_network.grid.delta_theta
    number_of_phase = len(reluctance_network.get_element((0,0)).stator_excitation_coeffs)
    airgap_flux_density = None
    flux_linkage = np.zeros((number_of_phase+1, n_point_standard))
    coenergy = np.zeros((2, n_point_cogging))
    torque_maxwell_stress_tensor = np.zeros((2, n_point_cogging))
    cogging_shifted = 0
    time_start = time.perf_counter()
    with tqdm(range(n_point_check), desc=" Solving", **TQDM_KWARGS) as pbar:
        for i in pbar:
            if i == 0:
                reluctance_network = fixed_point_iteration(reluctance_network,detail_debug=debug,first_step = True)
                airgap_flux_density = reluctance_network.export_flux_density(position = airgap_position)
                coenergy[-1,0] = 0 
                coenergy[0,0] = reluctance_network.coenergy()
                torque_maxwell_stress_tensor[-1,0] = 0
                torque_maxwell_stress_tensor[0,0] = reluctance_network.maxwell_stress_tensor(airgap_position)
                flux_linkage[-1,0] = 0
                flux_linkage_position = reluctance_network.flux_linkage()*spm.reduce_factor
                for k in range(number_of_phase): flux_linkage[k,0] = flux_linkage_position[k]
            else:
                if i < n_point_cogging:
                    reluctance_network.shift_element(ring_shift, step_cogging)
                    cogging_shifted += step_cogging
                    reluctance_network = fixed_point_iteration(reluctance_network,detail_debug=debug)
                    coenergy[-1,i] = i*theta_resolution
                    coenergy[0,i] = reluctance_network.coenergy()
                    torque_maxwell_stress_tensor[-1,i] = i*theta_resolution
                    torque_maxwell_stress_tensor[0,i] = reluctance_network.maxwell_stress_tensor(airgap_position)
                    if i % step_standard == 0:
                        cogging_shifted -= step_standard
                        j = i//step_standard
                        flux_linkage[-1,j] = i*theta_resolution*step_cogging
                        flux_linkage_position = reluctance_network.flux_linkage()*spm.reduce_factor
                        for k in range(number_of_phase): flux_linkage[k,j] = flux_linkage_position[k]
                else:
                    if i % step_standard == 0:
                        j = i//step_standard
                        flux_linkage[-1,j] = i*theta_resolution*step_cogging
                        reluctance_network.shift_element(ring_shift, int(step_standard - cogging_shifted))
                        reluctance_network = fixed_point_iteration(reluctance_network,detail_debug=debug)
                        cogging_shifted = 0
                        flux_linkage_position = reluctance_network.flux_linkage()*spm.reduce_factor
                        for k in range(number_of_phase): flux_linkage[k,j] = flux_linkage_position[k]
    total_time =  time.perf_counter()-time_start
    print(total_time,"second")
    coenergy = duplicate_periodic_data(coenergy)
    torque_maxwell_stress_tensor = duplicate_periodic_data(torque_maxwell_stress_tensor)
    torque_maxwell_stress_tensor[0] = torque_maxwell_stress_tensor[0] * spm.reduce_factor
    if show_plot:
        plot_data.append({
            "x": airgap_flux_density[-1,:],
            "y": [airgap_flux_density[0,:], airgap_flux_density[1,:], airgap_flux_density[2,:]],
            "labels": ["B_avg","B_radial","B_tangential"],
            "title": "Air-gap Flux Density vs Rotor Angle",
            "xlabel": "Rotor angle (rad)",
            "ylabel": "Flux Density (T)"
        })
        plot_data.append({
            "x": torque_maxwell_stress_tensor[1,:],
            "y": [torque_maxwell_stress_tensor[0,:]],
            "labels": ["Torque (Maxwell Stress Tensor)"],
            "title": "Electromagnetic Torque (Maxwell Stress Tensor)",
            "xlabel": "Rotor angle (rad)",
            "ylabel": "Torque (Nm)"
        })
    cogging_torque = np.array([])
    valid_co_idx = np.where(np.logical_or(coenergy[1,:]!=0.0,np.arange(coenergy.shape[1])==0))[0]
    if valid_co_idx.size>=2 and solve_cogging_torque:
        theta_co = coenergy[1,valid_co_idx]
        co_w = coenergy[0,valid_co_idx]*getattr(spm,"reduce_factor",1.0)
        if show_plot:
            plot_data.append({"x":theta_co,"y":[co_w],"labels":["Co-energy"],"title":"Co-energy vs Rotor Angle","xlabel":"Rotor angle (rad)","ylabel":"Co-energy (J)"})
        coenergy_data = np.vstack([co_w,theta_co])
        d_co = periodic_derivative(coenergy_data)
        torque = d_co[0]
        cogging_torque = np.vstack([torque,theta_co])
        if show_plot:
            plot_data.append({"x":theta_co,"y":[torque],"labels":["Cogging Torque"],"title":"Cogging Torque vs Rotor Angle","xlabel":"Rotor angle (rad)","ylabel":"Cogging Torque (Nm)"})
    valid_flux_idx = np.where(np.logical_or(flux_linkage[-1,:]!=0.0,np.arange(flux_linkage.shape[1])==0))[0]
    back_emf_phase = np.zeros((number_of_phase+1,len(valid_flux_idx))) if valid_flux_idx.size>0 else np.array([[]])
    back_emf_line = np.zeros((4,len(valid_flux_idx))) if valid_flux_idx.size>0 and number_of_phase==3 else np.array([[]])
    if valid_flux_idx.size>=1 and solve_flux_linkage:
        theta_flux = flux_linkage[-1,valid_flux_idx]
        flux_data = flux_linkage[:-1,valid_flux_idx]
        if solve_back_emf_phase or solve_back_emf_line:
            w_shaft = getattr(spm,"shaft_speed",0.0)*2*pi/60.0
            flux_full = np.vstack([flux_data,theta_flux])
            d_flux = periodic_derivative(flux_full)
            dphi_dtheta = d_flux[:-1,:] if d_flux.shape[0]==flux_full.shape[0] else d_flux
            back_emf_arr = w_shaft*dphi_dtheta
            back_emf_phase = np.vstack([back_emf_arr,theta_flux])
            if number_of_phase==3 and solve_back_emf_line:
                V_ab = back_emf_arr[0]-back_emf_arr[1]
                V_bc = back_emf_arr[1]-back_emf_arr[2]
                V_ca = back_emf_arr[2]-back_emf_arr[0]
                back_emf_line = np.vstack([V_ab,V_bc,V_ca,theta_flux])
                if show_plot:
                    plot_data.append({"x":theta_flux,"y":[V_ab,V_bc,V_ca],"labels":["V_ab","V_bc","V_ca"],"title":"Line-to-Line Back EMF","xlabel":"Rotor angle (rad)","ylabel":"Line-to-Line Back EMF (V)"})
            if show_plot:
                plot_data.append({"x":theta_flux,"y":[back_emf_arr[k] for k in range(back_emf_arr.shape[0])],"labels":[f"Phase {k+1}" for k in range(back_emf_arr.shape[0])],"title":"Phase Back EMF","xlabel":"Rotor angle (rad)","ylabel":"Back EMF (V)"})
    if show_plot:
        for item in plot_data:
            plt.figure(figsize=(8,5))
            for y,label in zip(item["y"],item["labels"]): plt.plot(item["x"],y,label=label)
            plt.xlabel(item["xlabel"]); plt.ylabel(item["ylabel"]); plt.title(item["title"]); plt.legend(); plt.grid(True); plt.tight_layout()
        plt.show()
        reluctance_network.view_flux_density(show_plot=show_plot)
        
    if angle_unit=="degree":
        airgap_flux_density[-1]*=180/pi*spm.reduce_factor
        flux_linkage[-1]*=180/pi*spm.reduce_factor
        back_emf_phase[-1]*=180/pi*spm.reduce_factor
        back_emf_line[-1]*=180/pi*spm.reduce_factor
        cogging_torque[-1]*=180/pi
        torque_maxwell_stress_tensor[-1]*= 180/pi
    if angle_unit=="radian":
        airgap_flux_density[-1]*=spm.reduce_factor
        flux_linkage[-1]*=spm.reduce_factor
        back_emf_phase[-1]*=spm.reduce_factor
        back_emf_line[-1]*=spm.reduce_factor
    return Output(airgap_flux_density = airgap_flux_density,
                  flux_linkage = flux_linkage,
                  back_emf_phase = back_emf_phase,
                  back_emf_line = back_emf_line,
                  cogging_torque = cogging_torque,
                  torque_maxwell_stress_tensor = torque_maxwell_stress_tensor,
                  total_time = total_time,
                  element_number = (reluctance_network.size [0] * reluctance_network.size[1]) )

class Output:
    def __init__(self, airgap_flux_density=None, flux_linkage=None, back_emf_phase=None, back_emf_line=None, cogging_torque=None, torque_maxwell_stress_tensor=None,total_time = None,element_number = None):
        self.airgap_flux_density = airgap_flux_density
        self.flux_linkage = flux_linkage
        self.back_emf_phase = back_emf_phase
        self.back_emf_line = back_emf_line
        self.cogging_torque = cogging_torque
        self.torque_maxwell_stress_tensor = torque_maxwell_stress_tensor
        self.total_time = total_time
        self.element_number = element_number
    