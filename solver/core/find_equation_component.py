import numpy as np
import scipy.sparse as sp
from solver.utils.get_linear_index import get_linear_index
from solver.utils.get_virtual_position import get_virtual_position
from solver.models.VirtualArray import VirtualArray

def find_equation_component(reluctance_network,
                    find_R = True, 
                    P = None,
                    find_F = True,
                    find_J = True,
                    find_G = True,
                    F_input = None ):
    
    cyclic_type = reluctance_network.cyclic_type
    loop_flux_array_virtual_size = reluctance_network.loop_flux_array.virtual_size
    loop_flux_array_1D_size = loop_flux_array_virtual_size[0] * loop_flux_array_virtual_size[1]

    if P is None:
        P = reluctance_network.loop_flux_array
    else:
        P = VirtualArray(P,loop_flux_array_virtual_size,cyclic_type)
        reluctance_network.loop_flux_array = P

    if find_R == True:
        R_row, R_col, R_data = [], [], []
    else: 
        R = []

    if find_F == True:
        F = np.zeros(loop_flux_array_1D_size)
    else:
        F = []

    if find_J == True:
        J_row, J_col, J_data = [], [], []
    else:
        J = []
    
    if find_G == True: 
        G = np.zeros(loop_flux_array_1D_size)
    else:
        G = []
        
    for k in range(loop_flux_array_1D_size):
        R_r,R_b,R_t,R_l = 0.0,0.0,0.0,0.0
        i, j = get_virtual_position(k, loop_flux_array_virtual_size)
        phi_c = k
        phi_t    = get_linear_index((i+1,j), loop_flux_array_virtual_size,cyclic_type)
        phi_b = get_linear_index((i-1,j), loop_flux_array_virtual_size,cyclic_type)
        phi_r  = get_linear_index((i,j+1), loop_flux_array_virtual_size,cyclic_type)
        phi_l   = get_linear_index((i,j-1), loop_flux_array_virtual_size,cyclic_type)
        NE = reluctance_network.get_element((i+1,j+1))
        NW = reluctance_network.get_element((i+1,j))
        SE = reluctance_network.get_element((i,j+1))
        SW = reluctance_network.get_element((i,j))

        if find_R == True:
            # R_phi_c
            R_row.append(phi_c)
            R_col.append(phi_c)
            R_c =(NW.reluctance_right_value[0] + NW.reluctance_bottom_value[0] +
                NE.reluctance_left_value[0] + NE.reluctance_bottom_value[0] +
                SE.reluctance_top_value[0] + SE.reluctance_left_value[0] +
                SW.reluctance_right_value[0] + SW.reluctance_top_value[0])
            R_data.append(float(R_c))

            # Gán R_phi_t
            if phi_t is not None :
                R_row.append(phi_c)
                R_col.append(phi_t)
                R_t = - NW.reluctance_right_value[0] - NE.reluctance_left_value[0]
                R_data.append(float(R_t))
            
            # Gán R_phi_r
            if phi_r is not None : 
                R_row.append(phi_c)
                R_col.append(phi_r)
                R_r = - NE.reluctance_bottom_value[0] - SE.reluctance_top_value[0]
                R_data.append(float(R_r))

            # Gán R_phi_b
            if phi_b is not None : 
                R_row.append(phi_c)
                R_col.append(phi_b)
                R_b =  - SE.reluctance_left_value[0] - SW.reluctance_right_value[0]
                R_data.append(float(R_b))

            # Gán R_phi_l
            if phi_l is not None :
                R_row.append(phi_c)
                R_col.append(phi_l)
                R_l = - SW.reluctance_top_value[0] - NW.reluctance_bottom_value[0]
                R_data.append(float(R_l))

        if find_F == True: 
            F_c = (
                  NW.mmf_source_right
                + NE.mmf_source_left
                - NE.mmf_source_bottom
                - SE.mmf_source_top
                - SE.mmf_source_left
                - SW.mmf_source_right
                + SW.mmf_source_top
                + NW.mmf_source_bottom
            )
            
            F[phi_c] = float(F_c)

        if find_G == True:
            if find_F == True and find_R == True:
                G[phi_c] =  R_c * P.get_1D(phi_c)
                if phi_t is not None:
                    G[phi_c] = G[phi_c] + R_t + P.get_1D(phi_t)
                if phi_r is not None:
                    G[phi_c] = G[phi_c] + R_r + P.get_1D(phi_r)
                if phi_b is not None:
                    G[phi_c] = G[phi_c] + R_b + P.get_1D(phi_b)
                if phi_b is not None:
                    G[phi_c] = G[phi_c] + R_l + P.get_1D(phi_l)

                G[phi_c] = G[phi_c] - F[phi_c]

            elif find_F == False and find_R == True:
                G[phi_c] =  R_c * P.get_1D(phi_c)
                if phi_t is not None:
                    G[phi_c] = G[phi_c] + R_t + P.get_1D(phi_t)
                if phi_r is not None:
                    G[phi_c] = G[phi_c] + R_r + P.get_1D(phi_r)
                if phi_b is not None:
                    G[phi_c] = G[phi_c] + R_b + P.get_1D(phi_b)
                if phi_b is not None:
                    G[phi_c] = G[phi_c] + R_l + P.get_1D(phi_l)

                G[phi_c] = G[phi_c] - F_input[phi_c]
                
        if find_J == True:
            # gán cho phi_c
            J_row.append(phi_c)
            J_col.append(phi_c)

            J_c =  (NW.reluctance_right_value[1] + NW.reluctance_bottom_value[1] +
                    NE.reluctance_left_value[1] - NE.reluctance_bottom_value[1] -
                    SE.reluctance_top_value[1] - SE.reluctance_left_value[1] -
                    SW.reluctance_right_value[1] + SW.reluctance_top_value[1]) * P.get_1D(phi_c)
            
            if phi_t is not None: 
                J_c = J_c +  (NW.reluctance_right_value[1] +NE.reluctance_left_value[1])* P.get_1D(phi_t)

            if phi_r is not None:
                J_c = J_c + (- NE.reluctance_bottom_value[1] - SE.reluctance_top_value[1])*P.get_1D(phi_r)
            
            if phi_b is not None:
                J_c = J_c + (- SE.reluctance_left_value[1] - SW.reluctance_right_value[1])*P.get_1D(phi_b)

            if phi_l is not None:
                J_c = J_c + (SW.reluctance_top_value[1] + NW.reluctance_bottom_value[1])*P.get_1D(phi_l)

            J_c = J_c + R_c
            J_data.append(J_c)



            # gán cho phi top
            if phi_t is not None:
                J_row.append(phi_c)
                J_col.append(phi_t)
                J_t = (NW.reluctance_right_value[1] + NE.reluctance_left_value[1])*P.get_1D(phi_t)
                J_t = J_t + (- NW.reluctance_right_value[1] - NE.reluctance_left_value[1])*P.get_1D(phi_c)
                J_t = J_t + R_t
                J_data.append(J_t)

            # gán cho phi right
            if phi_r is not None:
                J_row.append(phi_c)
                J_col.append(phi_r)
                J_r = (- NE.reluctance_bottom_value[1] - SE.reluctance_top_value[1])*P.get_1D(phi_r)
                J_r = J_r + (NE.reluctance_bottom_value[1] + SE.reluctance_top_value[1])*P.get_1D(phi_c)
                J_r = J_r + R_r
                J_data.append(J_r)

            # gán cho phi bottom
            if phi_b is not None:
                J_row.append(phi_c)
                J_col.append(phi_b)
                J_b = (- SE.reluctance_left_value[1] - SW.reluctance_right_value[1]) * ( P.get_1D(phi_b) - P.get_1D(phi_c)) + R_b
                J_data.append(J_b)

            # gán cho phi left
            if phi_l is not None:
                J_row.append(phi_c)
                J_col.append(phi_l)
                J_l = (- SW.reluctance_top_value[1] - NW.reluctance_bottom_value[1]) * ( P.get_1D(phi_c) - P.get_1D(phi_l)) + R_l
                J_data.append(J_l)
    
    # Sau comment này thoát khỏi vòng for
    if find_R == True:
        R = sp.csr_matrix((R_data, (R_row, R_col)), shape=(loop_flux_array_1D_size, loop_flux_array_1D_size))
    if find_J == True:
        J = sp.csr_matrix((J_data, (J_row, J_col)), shape=(loop_flux_array_1D_size, loop_flux_array_1D_size))
    
    return R,F,J,G
