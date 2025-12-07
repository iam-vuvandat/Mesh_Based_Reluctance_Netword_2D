from motor_geometry.models.ReluctanceNetwork import ReluctanceNetwork
from solver.models.VirtualArray import VirtualArray
from solver.core.create_equation import create_equation
from solver.utils.find_adaptive_damping_factor import find_adaptive_damping_factor
import numpy as np
from scipy.sparse.linalg import spsolve
import time

def fixed_point_iteration(reluctance_network, iterations=20, max_relative_residual=0.01, detail_debug=False,first_step = False):
    
    time_begin = time.perf_counter()
    if reluctance_network.optimization == "standard":
        reluctance_network.set_iron_reluctance_minimum()

    deltas, rel_deltas, damping_history = [], [], []
    total_time = 0.0 
    time_for_update_reluctance = 0.0
    eq = None
    F = None
    eps = 1e-12
    for i in range(iterations):
        if i == 0 : 
            if reluctance_network.optimization == "standard":
                eq = create_equation(reluctance_network)
                R = eq.R
                F = eq.F
            elif reluctance_network.optimization == "vectorized":
                eq = create_equation(reluctance_network,first_time = True,create_F = True)
                R = eq.R
                F = eq.F
        else:
            if reluctance_network.optimization == "standard":
                eq = create_equation(reluctance_network,create_F = False)
                R = eq.R
            elif reluctance_network.optimization == "vectorized":
                eq = create_equation(reluctance_network,first_time = False,create_F = False)
                R = eq.R


        old_phi = np.ravel(reluctance_network.loop_flux_array.data).astype(float)
        new_phi = spsolve(R, F)
        new_phi = np.ravel(new_phi).astype(float)

        delta = np.linalg.norm(new_phi - old_phi)
        rel_delta = delta / (np.linalg.norm(old_phi) + eps)
        deltas.append(delta)
        rel_deltas.append(rel_delta)
        
        if i == 0:
            damping_factor = 1.0
        else:
            damping_factor = find_adaptive_damping_factor(rel_delta)
        damping_history.append(damping_factor)
        damped_phi = (1 - damping_factor) * old_phi + damping_factor * new_phi
        reluctance_network.loop_flux_array.data = damped_phi
        
        time_begin_update =time.perf_counter()
        reluctance_network.loop_flux_array = reluctance_network.loop_flux_array
        time_finish_update = time.perf_counter()
        time_for_update_reluctance += time_finish_update - time_begin_update

        if detail_debug:
            prefix = "\n" if i == 0 else ""
            print(f"{prefix}Step {i+1:02d}: damp={damping_factor:.3f}, full_delta={delta:.3e}, "
                  f"rel_delta={rel_delta*100:.4f}%")

        if rel_delta < max_relative_residual:
            if detail_debug:
                print(f"Converged at step {i+1}, relative delta = {rel_delta*100:.4f}% < {max_relative_residual*100:.4f}%")
            break

    time_finish = time.perf_counter() 
    total_time = time_finish - time_begin
    time_cost_for_update = (time_for_update_reluctance / total_time) * 100
    if detail_debug == True: 
        print(time_cost_for_update," %")
    
    return reluctance_network