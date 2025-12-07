import numpy as np
import scipy.sparse as sp
from solver.utils.get_linear_index import get_linear_index
from solver.utils.get_virtual_position import get_virtual_position
from solver.core.get_2D_index_vectorized import get_2D_index_vectorized
from solver.core.get_2D_value_vectorized import get_2D_value_vectorized
from solver.core.get_1D_index_vectorized import get_1D_index_vectorized
from solver.core.exclude_invalid_columns_vectorized import exclude_invalid_columns_vectorized

class EquationComponent:
    def __init__(self,R = None, F = None, J = None):
        self.R = R
        self.F = F
        self.J = J

def create_equation(reluctance_network,create_jacobian = False,first_time = False,create_F = True):
    """
    Tạo các ma trận:
    R: ma trận từ trở,
    F: ma trận nguồn sức từ động,
    J: ma trận jacobian
    """
    if reluctance_network.optimization == "standard":
        # Loại tuần hoàn:
        cyclic_type = reluctance_network.cyclic_type

        # Kích thước loop_flux_array:
        loop_flux_array_virtual_size = reluctance_network.loop_flux_array.virtual_size
        loop_flux_array_1D_size = loop_flux_array_virtual_size[0] * loop_flux_array_virtual_size[1]
    
        # lấy loop_flux:
        loop_flux = reluctance_network.loop_flux_array

        # Tạo mảng rỗng
        R_row, R_col, R_data = [], [], []
        F = np.zeros(loop_flux_array_1D_size)
        if create_jacobian == True:
            J_row, J_col, J_data = [], [], []

        for k in range(loop_flux_array_1D_size):

            # Lấy vị trí neighbor loop flux
            i, j = get_virtual_position(k, loop_flux_array_virtual_size)
            phi_c = k
            phi_t    = get_linear_index((i+1,j), loop_flux_array_virtual_size,cyclic_type)
            phi_b = get_linear_index((i-1,j), loop_flux_array_virtual_size,cyclic_type)
            phi_r  = get_linear_index((i,j+1), loop_flux_array_virtual_size,cyclic_type)
            phi_l   = get_linear_index((i,j-1), loop_flux_array_virtual_size,cyclic_type)

            # Lấy neighbor Element
            NE = reluctance_network.get_element((i+1,j+1))
            NW = reluctance_network.get_element((i+1,j))
            SE = reluctance_network.get_element((i,j+1))
            SW = reluctance_network.get_element((i,j))

            # R_phi_c
            R_row.append(phi_c)
            R_col.append(phi_c)

            data0 = 0.0
            data0 = data0 + NW.reluctance_right_value[0] + NW.reluctance_bottom_value[0]
            data0 = data0 + NE.reluctance_left_value[0] + NE.reluctance_bottom_value[0]
            data0 = data0 + SE.reluctance_top_value[0] + SE.reluctance_left_value[0]
            data0 = data0 + SW.reluctance_right_value[0] + SW.reluctance_top_value[0]

            R_data.append(float(data0))

            # Gán R_phi_t
            if phi_t is not None :
                R_row.append(phi_c)
                R_col.append(phi_t)

                data1 = 0.0
                data1 = data1 - NW.reluctance_right_value[0] 
                data1 = data1 - NE.reluctance_left_value[0]

                R_data.append(float(data1))
            
            # Gán R_phi_r
            if phi_r is not None : 
                R_row.append(phi_c)
                R_col.append(phi_r)

                data2 = 0.0
                data2 = data2 - NE.reluctance_bottom_value[0]
                data2 = data2 - SE.reluctance_top_value[0]

                R_data.append(float(data2))

            # Gán R_phi_b
            if phi_b is not None : 
                R_row.append(phi_c)
                R_col.append(phi_b)

                data3 = 0.0
                data3 = data3 - SE.reluctance_left_value[0]
                data3 = data3 - SW.reluctance_right_value[0]

                R_data.append(float(data3))

            # Gán R_phi_l
            if phi_l is not None :
                R_row.append(phi_c)
                R_col.append(phi_l)

                data4 = 0.0
                data4 = data4 - SW.reluctance_top_value[0]
                data4 = data4 - NW.reluctance_bottom_value[0]
                
                R_data.append(float(data4))
            
            # Gán F
            if create_F == True:
                data5 = 0 
                data5 = data5 + NW.mmf_source_right 
                data5 = data5 + NE.mmf_source_left

                data5 = data5 - NE.mmf_source_bottom
                data5 = data5 - SE.mmf_source_top

                data5 = data5 - SE.mmf_source_left
                data5 = data5 - SW.mmf_source_right

                data5 = data5 + SW.mmf_source_top
                data5 = data5 + NW.mmf_source_bottom

                F[phi_c] = float(data5)

            
        
            if create_jacobian == True:
                # Tạo ma trận Jacobian
                # Gán J_phi_c
                J_row.append(phi_c)
                J_col.append(phi_c)
                data6 = 0 
                data6 = data6 + data0 

                # Đạo hàm thành phần R_phi_c theo phi_c và nhân với phi_c:

                drc_dpc = 0.0
                drc_dpc = drc_dpc + NW.reluctance_right_value[1] + NW.reluctance_bottom_value[1]
                drc_dpc = drc_dpc + NE.reluctance_left_value[1] - NE.reluctance_bottom_value[1]
                drc_dpc = drc_dpc - SE.reluctance_top_value[1] - SE.reluctance_left_value[1]
                drc_dpc = drc_dpc - SW.reluctance_right_value[1] + SW.reluctance_top_value[1]
                drc_dpc = drc_dpc * loop_flux.get_1D(phi_c) # nhân với phi_c

                # Đạo hàm thành phần R_phi_t theo phi c rồi nhân với phi_t
                drt_dpc = 0.0
                if phi_t is not None:
                    drt_dpc = drt_dpc - NW.reluctance_right_value[1]
                    drt_dpc = drt_dpc - NE.reluctance_left_value[1]
                    drt_dpc = drt_dpc * loop_flux.get_1D(phi_t) # *

                # Đạo hàm thành phần R_phi_r theo phi_c rồi nhân phi_r
                drr_dpc = 0.0
                if phi_r is not None: 
                    drr_dpc = drr_dpc + NE.reluctance_bottom_value[1]
                    drr_dpc = drr_dpc + SE.reluctance_top_value[1]
                    drr_dpc = drr_dpc * loop_flux.get_1D(phi_r)

                # Đạo hàm thành phần R_phi_b theo phi_c rồi nhân phi_b
                drb_dpc = 0.0 
                if phi_b is not None: 
                    drb_dpc = drb_dpc + SE.reluctance_left_value[1]       
                    drb_dpc = drb_dpc + SW.reluctance_right_value[1]
                    drb_dpc = drb_dpc * loop_flux.get_1D(phi_b)

                # Đạo hàm thành phần R_phi_l theo phi_c rồi nhân phi_l
                drl_dpc = 0.0
                if phi_l is not None:
                    drl_dpc = drl_dpc  - SW.reluctance_top_value[1]
                    drl_dpc = drl_dpc  - NW.reluctance_bottom_value[1]
                    drl_dpc = drl_dpc * loop_flux.get_1D(phi_l)
                
                J_data.append(float(data6 + drc_dpc + drt_dpc + drr_dpc+ drb_dpc + drl_dpc))

                # Thành phần top trong jacobian
                if phi_t is not None: 
                    J_row.append(phi_c)
                    J_col.append(phi_t)

                    data7 = 0.0 
                    data7 = data7+ data1 # Thành phần R tương ứng

                    # Đạo hàm R_phi_c theo phi_t rôi nhân với phi_c
                    drc_dpt = 0 
                    drc_dpt = drc_dpt - NW.reluctance_right_value[1]
                    drc_dpt = drc_dpt - NE.reluctance_left_value[1]
                    drc_dpt = drc_dpt * loop_flux.get_1D(phi_c)

                    #Đạo hàm R_phi_t theo phi_t rôi nhân phi_t
                    drt_dpt = 0.0
                    drt_dpt = drt_dpt + NW.reluctance_right_value[1]
                    drt_dpt = drt_dpt + NE.reluctance_left_value[1]
                    drt_dpt = drt_dpt * loop_flux.get_1D(phi_t)
                    ## Quy luật: 2 thành phần drc_dpt và drt_dpt triệt tiêu:)))))
                    ## Các hướng khác áp dụng tương tự
                    J_data.append(float(data7)) 
                # Thành phần right trong jacobian
                if phi_r is not None:
                    J_row.append(phi_c)
                    J_col.append(phi_r)
                    J_data.append(float(data2))

                if phi_b is not None:
                    J_row.append(phi_c)
                    J_col.append(phi_b)
                    J_data.append(float(data3))
                if phi_l is not None:
                    J_row.append(phi_c)
                    J_col.append(phi_l)
                    J_data.append(float(data4))

        # Sau comment này thoát khỏi vòng for
        R = sp.csr_matrix((R_data, (R_row, R_col)), shape=(loop_flux_array_1D_size, loop_flux_array_1D_size))
        if create_jacobian == True:
            J = sp.csr_matrix((J_data, (J_row, J_col)), shape=(loop_flux_array_1D_size, loop_flux_array_1D_size))
        else:
            J = []
        return EquationComponent(R = R, F = F, J = J)
    




    elif reluctance_network.optimization == "vectorized":
        if first_time == True:
            use_minimum_reluctance = True
        else:
            use_minimum_reluctance = False
        eq= reluctance_network.vectorized_element.export_equation(create_F = True,
                                                                    use_minimum_reluctance =use_minimum_reluctance)
        R = eq.R
        F = eq.F                                                     

        
        return EquationComponent(F=F,R=R)
    
        