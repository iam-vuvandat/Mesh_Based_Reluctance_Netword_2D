import numpy as np 
import math
from solver.core.exclude_invalid_columns_vectorized import exclude_invalid_columns_vectorized
from solver.core.get_1D_index_vectorized import get_1D_index_vectorized
from solver.core.get_2D_index_vectorized import get_2D_index_vectorized
from solver.core.get_2D_value_vectorized import get_2D_value_vectorized
from material_data.core.lookup_BH_curve import lookup_BH_curve
import scipy.sparse as sp

class VectorizedElement:
    def __init__(self,reluctance_network):
        """
        Phiên bản vectorized (hiệu suất cao) của Element, phá bỏ tạm thời tính hướng đối tượng của các Element
        Tốc độ xử lý cao hơn rất nhiều so với truy cập thuộc tính 
        """
        self.reluctance_network_size            = reluctance_network.size
        self.element_number                     = int(self.reluctance_network_size[0] * self.reluctance_network_size[1])
        self.phase_number                       = len(reluctance_network.elements[0].stator_excitation_coeffs)
        self.cyclic_type                        = reluctance_network.cyclic_type
        self.phi_loop_size                      = reluctance_network.loop_flux_array.size
        self.phi_loop_virtual_size              = reluctance_network.loop_flux_array.virtual_size
        self.material_database                  = reluctance_network.material_database
        self.element_index                      = np.arange(0,self.element_number)
        self.loop_flux_index                    = np.arange(0,self.phi_loop_size)
        self.theta_resolution                   = reluctance_network.theta_resolution

        self.create_vectorized_element(reluctance_network)
        self.update_reluctance(reluctance_network)
        self.update_mmf_source(reluctance_network)
    
    def create_vectorized_element(self,reluctance_network):
        self.material                   = np.zeros((self.element_number,), dtype=int)

        self.axial_length               = np.zeros((self.element_number,), dtype=float)

        self.average_radius             = np.zeros((self.element_number,), dtype=float)

        self.magnet_source              = np.zeros((4,self.element_number))
        self.delta_angle_winding_factor = np.zeros((4,self.element_number))
        self.area_invert                = np.zeros((4,self.element_number))
        self.average_area_invert        = np.zeros((2,self.element_number))
        self.vacuum_reluctance          = np.zeros((4,self.element_number))
        self.reluctance_minimum         = np.zeros((4,self.element_number))
        self.stator_excitation_coeffs   = np.zeros((self.phase_number,self.element_number))
        
        self.flux_direct                = np.zeros((4,self.element_number))
        self.flux_density_direct        = np.zeros((4,self.element_number))
        self.relative_permeance_invert  = np.zeros((4,self.element_number))
        self.flux_density_average       = np.zeros((3,self.element_number))
        self.reluctance                 = np.zeros((4,self.element_number))
        self.winding_direct_source      = np.zeros((4,self.element_number))
        self.mmf_source                 = np.zeros((4,self.element_number))

        self.virtual_index_element,_ = get_2D_index_vectorized(self.element_index,
                                                                 virtual_size=self.reluctance_network_size,
                                                                 offset_vector=(0,0),
                                                                 cyclic_type="no_cyclic")
        self.virtual_index_flux_loop,_ = get_2D_index_vectorized(index_1D_input= self.loop_flux_index,
                                                                virtual_size= self.phi_loop_virtual_size,
                                                                offset_vector=(0,0),
                                                                cyclic_type="no_cyclic")

        for i in range(self.element_number):
            element = reluctance_network.elements[i]

            self.material[i]                       = int(element.material_numeric_format)

            self.axial_length[i]                   = element.axial_length

            self.average_radius[i]                 = element.average_radius

            self.magnet_source[0, i]               = element.magnet_source_top
            self.magnet_source[1, i]               = element.magnet_source_right
            self.magnet_source[2, i]               = element.magnet_source_bottom
            self.magnet_source[3, i]               = element.magnet_source_left

            self.delta_angle_winding_factor[0, i]  = element.half_cos_delta_angle_stator_excitation
            self.delta_angle_winding_factor[1, i]  = element.half_sin_delta_angle_stator_excitation
            self.delta_angle_winding_factor[2, i]  = element.half_cos_delta_angle_stator_excitation
            self.delta_angle_winding_factor[3, i]  = element.half_sin_delta_angle_stator_excitation

            self.area_invert[0, i]                 = element.area_top_invert
            self.area_invert[1, i]                 = element.area_right_invert
            self.area_invert[2, i]                 = element.area_bottom_invert
            self.area_invert[3, i]                 = element.area_left_invert

            self.average_area_invert[0, i]         = element.area_radial_invert
            self.average_area_invert[1, i]         = element.area_tangential_invert

            self.vacuum_reluctance[0, i]           = element.vacuum_reluctance_top
            self.vacuum_reluctance[1, i]           = element.vacuum_reluctance_right
            self.vacuum_reluctance[2, i]           = element.vacuum_reluctance_bottom
            self.vacuum_reluctance[3, i]           = element.vacuum_reluctance_left

            self.reluctance_minimum[0, i]          = element.reluctance_minimum_top
            self.reluctance_minimum[1, i]          = element.reluctance_minimum_right
            self.reluctance_minimum[2, i]          = element.reluctance_minimum_bottom
            self.reluctance_minimum[3, i]          = element.reluctance_minimum_left

            for j in range(self.phase_number):
                self.stator_excitation_coeffs[j,i] = float(element.stator_excitation_coeffs[j])

            

    def update_reluctance(self,reluctance_network):
        loop_flux = reluctance_network.loop_flux_array.data.ravel()

        phi_ne,_ = get_2D_value_vectorized(data= loop_flux,
                                            index_2D= self.virtual_index_element,
                                            virtual_size= self.phi_loop_virtual_size,
                                            offset_vector=(0,0),
                                            cyclic_type= self.cyclic_type)
        phi_se,_ = get_2D_value_vectorized(data= loop_flux,
                                            index_2D= self.virtual_index_element,
                                            virtual_size= self.phi_loop_virtual_size,
                                            offset_vector=(-1,0),
                                            cyclic_type= self.cyclic_type)
        phi_sw,_ = get_2D_value_vectorized(data= loop_flux,
                                            index_2D= self.virtual_index_element,
                                            virtual_size= self.phi_loop_virtual_size,
                                            offset_vector=(-1,-1),
                                            cyclic_type= self.cyclic_type)
        phi_nw,_ = get_2D_value_vectorized(data= loop_flux,
                                            index_2D= self.virtual_index_element,
                                            virtual_size= self.phi_loop_virtual_size,
                                            offset_vector=(0,-1),
                                            cyclic_type= self.cyclic_type)
        
        self.flux_direct[0] = phi_ne - phi_nw
        self.flux_direct[1] = phi_se - phi_ne
        self.flux_direct[2] = phi_se - phi_sw
        self.flux_direct[3] = phi_sw - phi_nw


        self.flux_density_direct = self.flux_direct * self.area_invert
        self.flux_density_average[0] = (self.flux_direct[0] + self.flux_direct[2]) * self.average_area_invert[0]
        self.flux_density_average[1] = -(self.flux_direct[1] + self.flux_direct[3]) * self.average_area_invert[1]
        self.flux_density_average[2] = np.sqrt(self.flux_density_average[0]**2 + self.flux_density_average[1]**2)

        self.relative_permeance_invert,_ = lookup_BH_curve(B_input= self.flux_density_direct,
                                                         material_database= self.material_database,
                                                         return_du_dB= False,
                                                         material_filter= self.material,
                                                         invert = True)
        
        self.reluctance = self.vacuum_reluctance * self.relative_permeance_invert


    def update_mmf_source(self, reluctance_network):
        stator_excitation = reluctance_network.stator_excitation.ravel()
        self.winding_excitation = stator_excitation @ self.stator_excitation_coeffs
        self.winding_direct_source = self.delta_angle_winding_factor * self.winding_excitation
        self.mmf_source = self.winding_direct_source + self.magnet_source
        

    def apply_vectorized_element(self,reluctance_network):
        for i in range(self.element_number):
            if self.material[i] == 0:
                reluctance_network.elements[i].material = "air"
            elif self.material[i] == 1:
                reluctance_network.elements[i].material = "magnet"
            elif self.material[i] == 2:
                reluctance_network.elements[i].material = "iron"

            for j in range(self.phase_number):
                reluctance_network.elements[i].stator_excitation_coeffs[j] = self.stator_excitation_coeffs[j,i]

            
    
    def shift(self, ring_shift, direction=1):
        """
        Xoay các element trong mạng vectorized.
        - ring_shift: tuple (begin, end) chỉ hàng/cột cần xoay
        - direction: số bước xoay, dương nghĩa là sang phải/xuống, âm là trái/lên
        Dữ liệu được xoay:
        self.material, self.magnet_source, self.delta_angle_winding_factor,
        self.area_invert, self.average_area_invert, self.vacuum_reluctance,
        self.reluctance_minimum, self.stator_excitation_coeffs, self.mmf_source
        """

        number_of_rows, number_of_cols = self.reluctance_network_size
        ring_begin, ring_end = ring_shift

        # giới hạn ring_shift trong biên
        ring_begin = max(0, ring_begin)
        ring_end = min((number_of_rows if self.cyclic_type=="second_dimension" else number_of_cols) - 1, ring_end)
        
        # Chuyển tất cả dữ liệu cần shift sang dạng ma trận (shape phù hợp)
        # 1D dữ liệu (self.material): (rows, cols)
        material_2D = self.material.reshape(number_of_rows, number_of_cols)
        
        # 2D dữ liệu (shape: n_properties x n_elements)
        def reshape_prop(prop, n_rows, n_cols):
            return prop.reshape((prop.shape[0], n_rows, n_cols))
        
        magnet_source_3D = reshape_prop(self.magnet_source, number_of_rows, number_of_cols)
        delta_angle_3D = reshape_prop(self.delta_angle_winding_factor, number_of_rows, number_of_cols)
        area_invert_3D = reshape_prop(self.area_invert, number_of_rows, number_of_cols)
        average_area_2D = reshape_prop(self.average_area_invert, number_of_rows, number_of_cols)
        vacuum_3D = reshape_prop(self.vacuum_reluctance, number_of_rows, number_of_cols)
        rel_min_3D = reshape_prop(self.reluctance_minimum, number_of_rows, number_of_cols)
        stator_exc_2D = reshape_prop(self.stator_excitation_coeffs, number_of_rows, number_of_cols)
        mmf_3D = reshape_prop(self.mmf_source, number_of_rows, number_of_cols)

        # Tính shift theo cyclic_type
        if self.cyclic_type == "first_dimension":
            # shift theo cột
            direction_mod = direction % number_of_cols
            rows = np.arange(ring_begin, ring_end+1)

            # 1D
            material_2D[rows, :] = np.roll(material_2D[rows, :], shift=direction_mod, axis=1)
            # 3D: giữ axis 0 (thuộc tính), shift theo axis 2 (cột)
            magnet_source_3D[:, rows, :] = np.roll(magnet_source_3D[:, rows, :], shift=direction_mod, axis=2)
            delta_angle_3D[:, rows, :] = np.roll(delta_angle_3D[:, rows, :], shift=direction_mod, axis=2)
            area_invert_3D[:, rows, :] = np.roll(area_invert_3D[:, rows, :], shift=direction_mod, axis=2)
            average_area_2D[:, rows, :] = np.roll(average_area_2D[:, rows, :], shift=direction_mod, axis=2)
            vacuum_3D[:, rows, :] = np.roll(vacuum_3D[:, rows, :], shift=direction_mod, axis=2)
            rel_min_3D[:, rows, :] = np.roll(rel_min_3D[:, rows, :], shift=direction_mod, axis=2)
            stator_exc_2D[:, rows, :] = np.roll(stator_exc_2D[:, rows, :], shift=direction_mod, axis=2)
            mmf_3D[:, rows, :] = np.roll(mmf_3D[:, rows, :], shift=direction_mod, axis=2)

        elif self.cyclic_type == "second_dimension":
            # shift theo hàng
            direction_mod = direction % number_of_rows
            cols = np.arange(ring_begin, ring_end+1)

            # 1D
            material_2D[:, cols] = np.roll(material_2D[:, cols], shift=direction_mod, axis=0)
            # 3D: giữ axis 0 (thuộc tính), shift theo axis 1 (hàng)
            magnet_source_3D[:, :, cols] = np.roll(magnet_source_3D[:, :, cols], shift=direction_mod, axis=1)
            delta_angle_3D[:, :, cols] = np.roll(delta_angle_3D[:, :, cols], shift=direction_mod, axis=1)
            area_invert_3D[:, :, cols] = np.roll(area_invert_3D[:, :, cols], shift=direction_mod, axis=1)
            average_area_2D[:, :, cols] = np.roll(average_area_2D[:, :, cols], shift=direction_mod, axis=1)
            vacuum_3D[:, :, cols] = np.roll(vacuum_3D[:, :, cols], shift=direction_mod, axis=1)
            rel_min_3D[:, :, cols] = np.roll(rel_min_3D[:, :, cols], shift=direction_mod, axis=1)
            stator_exc_2D[:, :, cols] = np.roll(stator_exc_2D[:, :, cols], shift=direction_mod, axis=1)
            mmf_3D[:, :, cols] = np.roll(mmf_3D[:, :, cols], shift=direction_mod, axis=1)
        else:
            raise ValueError(f"cyclic_type phải là 'first_dimension' hoặc 'second_dimension', hiện là {self.cyclic_type}")

        # Flatten lại và gán về class
        self.material = material_2D.flatten()
        self.magnet_source = magnet_source_3D.reshape(self.magnet_source.shape)
        self.delta_angle_winding_factor = delta_angle_3D.reshape(self.delta_angle_winding_factor.shape)
        self.area_invert = area_invert_3D.reshape(self.area_invert.shape)
        self.average_area_invert = average_area_2D.reshape(self.average_area_invert.shape)
        self.vacuum_reluctance = vacuum_3D.reshape(self.vacuum_reluctance.shape)
        self.reluctance_minimum = rel_min_3D.reshape(self.reluctance_minimum.shape)
        self.stator_excitation_coeffs = stator_exc_2D.reshape(self.stator_excitation_coeffs.shape)
        self.mmf_source = mmf_3D.reshape(self.mmf_source.shape)

    def export_equation(self,create_F=True,use_minimum_reluctance = False):
        R = None
        R_row = None
        R_col = None
        R_data = None
        F = None
        NW_offset = (1,0)
        NE_offset = (1,1)
        SE_offset = (0,1)
        SW_offset = (0,0)

        top_index = 0 
        right_index = 1 
        bottom_index = 2 
        left_index = 3 

        if create_F ==True:
        
            F_NW_right,_ = get_2D_value_vectorized(data=self.mmf_source[right_index],
                                                   index_2D= self.virtual_index_flux_loop,
                                                   virtual_size= self.reluctance_network_size,
                                                   offset_vector=NW_offset,
                                                   cyclic_type= self.cyclic_type)
            
            F_NW_bottom,_ = get_2D_value_vectorized(data=self.mmf_source[bottom_index],
                                                   index_2D= self.virtual_index_flux_loop,
                                                   virtual_size= self.reluctance_network_size,
                                                   offset_vector=NW_offset,
                                                   cyclic_type= self.cyclic_type)
            
            F_NE_left,_ = get_2D_value_vectorized(data=self.mmf_source[left_index],
                                                   index_2D= self.virtual_index_flux_loop,
                                                   virtual_size= self.reluctance_network_size,
                                                   offset_vector=NE_offset,
                                                   cyclic_type= self.cyclic_type)
            F_NE_bottom,_ = get_2D_value_vectorized(data=self.mmf_source[bottom_index],
                                                   index_2D= self.virtual_index_flux_loop,
                                                   virtual_size= self.reluctance_network_size,
                                                   offset_vector=NE_offset,
                                                   cyclic_type= self.cyclic_type)
            
            F_SE_top,_ = get_2D_value_vectorized(data=self.mmf_source[top_index],
                                                   index_2D= self.virtual_index_flux_loop,
                                                   virtual_size= self.reluctance_network_size,
                                                   offset_vector=SE_offset,
                                                   cyclic_type= self.cyclic_type)
            
            F_SE_left,_ = get_2D_value_vectorized(data=self.mmf_source[left_index],
                                                   index_2D= self.virtual_index_flux_loop,
                                                   virtual_size= self.reluctance_network_size,
                                                   offset_vector=SE_offset,
                                                   cyclic_type= self.cyclic_type)
            
            F_SW_top,_ = get_2D_value_vectorized(data=self.mmf_source[top_index],
                                                   index_2D= self.virtual_index_flux_loop,
                                                   virtual_size= self.reluctance_network_size,
                                                   offset_vector=SW_offset,
                                                   cyclic_type= self.cyclic_type)
            F_SW_right,_ = get_2D_value_vectorized(data=self.mmf_source[right_index],
                                                   index_2D= self.virtual_index_flux_loop,
                                                   virtual_size= self.reluctance_network_size,
                                                   offset_vector=SW_offset,
                                                   cyclic_type= self.cyclic_type)
            
            F = F_NW_right + F_NE_left - F_NE_bottom - F_SE_top - F_SE_left - F_SW_right + F_SW_top + F_NW_bottom

        if use_minimum_reluctance == True:
            reluctance_data = self.reluctance_minimum
        else:
            reluctance_data = self.reluctance
        
        R_NW_right,_ = get_2D_value_vectorized(data=reluctance_data[right_index],
                                                index_2D= self.virtual_index_flux_loop,
                                                virtual_size= self.reluctance_network_size,
                                                offset_vector=NW_offset,
                                                cyclic_type= self.cyclic_type)
        
        R_NW_bottom,_ = get_2D_value_vectorized(data=reluctance_data[bottom_index],
                                                index_2D= self.virtual_index_flux_loop,
                                                virtual_size= self.reluctance_network_size,
                                                offset_vector=NW_offset,
                                                cyclic_type= self.cyclic_type)
        
        R_NE_left,_ = get_2D_value_vectorized(data=reluctance_data[left_index],
                                                index_2D= self.virtual_index_flux_loop,
                                                virtual_size= self.reluctance_network_size,
                                                offset_vector=NE_offset,
                                                cyclic_type= self.cyclic_type)
        
        R_NE_bottom,_ = get_2D_value_vectorized(data=reluctance_data[bottom_index],
                                                index_2D= self.virtual_index_flux_loop,
                                                virtual_size= self.reluctance_network_size,
                                                offset_vector=NE_offset,
                                                cyclic_type= self.cyclic_type)
        
        R_SE_top,_ = get_2D_value_vectorized(data=reluctance_data[top_index],
                                                index_2D= self.virtual_index_flux_loop,
                                                virtual_size= self.reluctance_network_size,
                                                offset_vector=SE_offset,
                                                cyclic_type= self.cyclic_type)
        R_SE_left,_ = get_2D_value_vectorized(data=reluctance_data[left_index],
                                                index_2D= self.virtual_index_flux_loop,
                                                virtual_size= self.reluctance_network_size,
                                                offset_vector=SE_offset,
                                                cyclic_type= self.cyclic_type)
        
        R_SW_top,_ = get_2D_value_vectorized(data=reluctance_data[top_index],
                                                index_2D= self.virtual_index_flux_loop,
                                                virtual_size= self.reluctance_network_size,
                                                offset_vector=SW_offset,
                                                cyclic_type= self.cyclic_type)
        R_SW_right,_ = get_2D_value_vectorized(data=reluctance_data[right_index],
                                                index_2D= self.virtual_index_flux_loop,
                                                virtual_size= self.reluctance_network_size,
                                                offset_vector=SW_offset,
                                                cyclic_type= self.cyclic_type)
        
        R_row = self.loop_flux_index
        R_col = self.loop_flux_index
        R_data = R_NW_right + R_NW_bottom + R_NE_left + R_NE_bottom + R_SE_top + R_SE_left + R_SW_top + R_SW_right
        
        phi_top_1D_index, phi_top_1D_valid = get_1D_index_vectorized(index_2D= self.virtual_index_flux_loop,
                                                   virtual_size= self.phi_loop_virtual_size,
                                                   offset_vector=(1,0),
                                                   cyclic_type=self.cyclic_type)
        
        R_top = -(R_NW_right + R_NE_left)
        row,col,data = exclude_invalid_columns_vectorized(self.loop_flux_index,
                                                          phi_top_1D_index,
                                                          R_top,
                                                          phi_top_1D_valid)
        R_row = np.hstack((R_row,row))
        R_col = np.hstack((R_col,col))
        R_data = np.hstack((R_data,data))

        phi_bottom_1D_index, phi_bottom_1D_valid = get_1D_index_vectorized(index_2D= self.virtual_index_flux_loop,
                                                   virtual_size= self.phi_loop_virtual_size,
                                                   offset_vector=(-1,0),
                                                   cyclic_type=self.cyclic_type)
        
        R_bottom = -(R_SW_right + R_SE_left)
        row,col,data = exclude_invalid_columns_vectorized(self.loop_flux_index,
                                                          phi_bottom_1D_index,
                                                          R_bottom,
                                                          phi_bottom_1D_valid)
        R_row = np.hstack((R_row,row))
        R_col = np.hstack((R_col,col))
        R_data = np.hstack((R_data,data))

        phi_right_1D_index, phi_right_1D_valid = get_1D_index_vectorized(index_2D= self.virtual_index_flux_loop,
                                                   virtual_size= self.phi_loop_virtual_size,
                                                   offset_vector=(0,1),
                                                   cyclic_type=self.cyclic_type)
        
        R_right = -(R_NE_bottom + R_SE_top)
        row,col,data = exclude_invalid_columns_vectorized(self.loop_flux_index,
                                                          phi_right_1D_index,
                                                          R_right,
                                                          phi_right_1D_valid)
        R_row = np.hstack((R_row,row))
        R_col = np.hstack((R_col,col))
        R_data = np.hstack((R_data,data))

        phi_left_1D_index, phi_left_1D_valid = get_1D_index_vectorized(index_2D= self.virtual_index_flux_loop,
                                                   virtual_size= self.phi_loop_virtual_size,
                                                   offset_vector=(0,-1),
                                                   cyclic_type=self.cyclic_type)
        
        R_left = -(R_NW_bottom + R_SW_top)
        row,col,data = exclude_invalid_columns_vectorized(self.loop_flux_index,
                                                          phi_left_1D_index,
                                                          R_left,
                                                          phi_left_1D_valid)
        R_row = np.hstack((R_row,row))
        R_col = np.hstack((R_col,col))
        R_data = np.hstack((R_data,data))

        R = sp.csr_matrix((R_data, (R_row, R_col)), shape=(self.phi_loop_size, self.phi_loop_size))

        return Output(R=R,F=F)
    
    def export_flux_density(self,slice_type = "row", position = 0 ):
        col_number = self.reluctance_network_size[1]
        if slice_type == "row":
            index_1D = np.arange(0,col_number)
            theta = index_1D * self.theta_resolution
            row_vector = np.full(col_number,position)
            element_in_slice_virtual_index = np.vstack((row_vector,index_1D))

            flux_density = np.zeros((3,col_number))

            flux_density[0],_ = get_2D_value_vectorized(data=self.flux_density_average[2],
                                                            index_2D= element_in_slice_virtual_index,
                                                            virtual_size= self.reluctance_network_size,
                                                            offset_vector= (0,0),
                                                            cyclic_type= "no_cyclic")
            flux_density[1],_ = get_2D_value_vectorized(data=self.flux_density_average[0],
                                                            index_2D= element_in_slice_virtual_index,
                                                            virtual_size= self.reluctance_network_size,
                                                            offset_vector= (0,0),
                                                            cyclic_type= "no_cyclic")
            flux_density[2],_ = get_2D_value_vectorized(data=self.flux_density_average[1],
                                                            index_2D= element_in_slice_virtual_index,
                                                            virtual_size= self.reluctance_network_size,
                                                            offset_vector= (0,0),
                                                            cyclic_type= "no_cyclic")

            return np.vstack((flux_density,theta))
        elif slice_type =="col":
            return None
        else:
            return None

    def flux_linkage(self):
        flux_across_winding = (0.5) * (self.flux_direct[0] + self.flux_direct[2])
        flux_linkage = self.stator_excitation_coeffs @ flux_across_winding.T
        return flux_linkage
    
    def torque_maxwell_stress_tensor(self,position):
        mu_0 = 4 * math.pi * 1e-7
        col_number = self.reluctance_network_size[1]
        col_index  = np.arange(0,col_number)
        row_index  = np.full(col_number,position)
        element_virtual_position = np.vstack((row_index,col_index))
        l = self.axial_length[0]

        r,_ = get_2D_value_vectorized(data = self.average_radius,
                                    index_2D= np.array([[position], [0]]),
                                    virtual_size = self.reluctance_network_size,
                                    offset_vector= (0,0),
                                    cyclic_type= "no_cyclic" ) 
    
        B_radial,_ = get_2D_value_vectorized(data=self.flux_density_average[0],
                                             index_2D= element_virtual_position,
                                             virtual_size= self.reluctance_network_size,
                                             offset_vector= (0,0),
                                             cyclic_type="no_cyclic")
        
        B_tangential,_ = get_2D_value_vectorized(data=self.flux_density_average[1],
                                                 index_2D= element_virtual_position,
                                             virtual_size= self.reluctance_network_size,
                                             offset_vector= (0,0),
                                             cyclic_type="no_cyclic")
        
        torque_factor = l * r**2 * self.theta_resolution /mu_0
        torque_component = B_radial * B_tangential
        
        torque = np.sum(torque_component * torque_factor )
        return -torque
    
class Output:
    def __init__(self,R = None, F = None ):
        self.R = R
        self.F = F





















































            
