import numpy as np
from motor_geometry.utils.extract_element_info import extract_element_info
from solver.utils.matrix_product import matrix_product
from motor_geometry.utils.compute_radial_area_annulus import compute_radial_area_annulus
from motor_geometry.utils.compute_tangential_area_annulus import compute_tangential_area_annulus
from motor_geometry.utils.compute_average_tangential_length import compute_average_tangential_length
from motor_geometry.utils.vacuum_reluctance import vacuum_reluctance
from material_data.models.MaterialDataBase import MaterialDataBase
from material_data.core.lookup_BH_curve import lookup_BH_curve
from material_data.utils.find_maximum_permeance import find_maximum_permeance
from matplotlib.patches import Polygon as MplPolygon
import matplotlib.pyplot as plt
from math import pi

class Element:
    def __init__(self, position, segments, grid, loop_flux_array, stator_excitation):
        """
        Class này chính là một Element (Phần tử trong mạng từ trở), làm các công việc sau:
        - Nhận thông tin về vị trí trong mạng từ trở, thông tin lưới, thông tin segments,...
          để tự xác định vật liệu, từ trở, nguồn từ hóa
        - Cung cấp các thông tin quan trọng để tối ưu hóa vectorized
        """  
        self.position = position
        self.material_database = MaterialDataBase()
        self.grid = grid 
        self._patch = None
        self._label_text = None
        self._label_text_visible = False

        (self.material, 
        self.index,    
        self.axial_length,
        self.magnetic_source, 
        self.delta_angle_magnetic_source, 
        self.stator_excitation_coeffs,  
        self.delta_angle_stator_excitation, 
        self.segment_first_dimension_length,  
        self.segment_opening_angle, 
        self.segment_second_dimension_length,
        self.inner_second_dimension,   
        self.outer_second_dimension,   
        self.first_dimension_length,   
        self.open_angle,                
        self.second_dimension_length
        ) = extract_element_info(position, grid, segments)

        if self.material == "air":
            self.material_numeric_format = 0
        elif self.material == "magnet":
            self.material_numeric_format = 1
        elif self.material == "iron":
            self.material_numeric_format = 2
        else:
            self.material_numeric_format = 0

        self.average_radius = (self.inner_second_dimension + self.outer_second_dimension)/2
        self.cos_delta_angle_stator_excitation = np.cos(self.delta_angle_stator_excitation)
        self.half_cos_delta_angle_stator_excitation = 0.5 * self.cos_delta_angle_stator_excitation
        self.sin_delta_angle_stator_excitation = np.sin(self.delta_angle_stator_excitation)
        self.half_sin_delta_angle_stator_excitation = 0.5 * self.sin_delta_angle_stator_excitation

        self._precompute_vacuum_reluctance() 
        self.material_database = MaterialDataBase() 
        self.update_from_flux_and_excitation(loop_flux_array, stator_excitation,update_reluctance = True, update_mmf_source = True)

        # Cập nhật ma trận dây quấn: 
        listt = []
        for ele in self.stator_excitation_coeffs:
            listt.append(ele* self.second_dimension_length/self.segment_second_dimension_length)
        self.stator_excitation_coeffs = listt

    def _precompute_vacuum_reluctance(self):
        if self.grid.type == "cartesian":
            # Dọc = second_dimension → top/bottom
            # Ngang = first_dimension → left/right
            area_vertical = self.first_dimension_length * self.axial_length
            area_horizontal = self.second_dimension_length * self.axial_length

            self.vacuum_reluctance_top = vacuum_reluctance(0.5*self.second_dimension_length, area_vertical)
            self.vacuum_reluctance_bottom = self.vacuum_reluctance_top
            self.vacuum_reluctance_left = vacuum_reluctance(0.5*self.first_dimension_length, area_horizontal)
            self.vacuum_reluctance_right = self.vacuum_reluctance_left

            self.area_top = area_vertical
            self.area_bottom = area_vertical
            self.area_left = area_horizontal
            self.area_right = area_horizontal

            self.length_top = 0.5*self.second_dimension_length
            self.length_bottom = self.length_top
            self.length_left = 0.5*self.first_dimension_length
            self.length_right = self.length_left

        elif self.grid.type == "polar":
            r_in = self.inner_second_dimension
            r_out = self.outer_second_dimension
            open_angle = self.open_angle
            axial_length = self.axial_length
            half_r = abs(0.5*(r_in - r_out))

            # Top/Bottom = radial (second_dimension)
            self.area_top = compute_radial_area_annulus(half_r, r_out, open_angle, axial_length)
            self.area_bottom = compute_radial_area_annulus(r_in, half_r, open_angle, axial_length)

            # Left/Right = tangential (first_dimension)
            self.area_left = compute_tangential_area_annulus(r_in, r_out, axial_length)
            self.area_right = self.area_left

            self.length_top = half_r
            self.length_bottom = half_r
            self.length_left = compute_average_tangential_length(r_in, r_out, open_angle/2)
            self.length_right = self.length_left

            self.vacuum_reluctance_top = vacuum_reluctance(half_r, self.area_top)
            self.vacuum_reluctance_bottom = vacuum_reluctance(half_r, self.area_bottom)
            self.vacuum_reluctance_left = vacuum_reluctance(self.length_left, self.area_left)
            self.vacuum_reluctance_right = self.vacuum_reluctance_left
        elif self.grid.type == "trapezoid":

            r_in = self.inner_second_dimension
            r_out = self.outer_second_dimension
            alpha_0 = self.open_angle

            self.area_top = self.axial_length * (1/2) * (3*r_out + r_in) * np.sin(alpha_0/2)
            self.area_bottom = self.axial_length * (1/2) * (r_out + 3*  r_in) * np.sin(alpha_0/2)

            self.area_right = self.second_dimension_length * self.axial_length
            self.area_left = self.area_right

            self.vacuum_reluctance_top = vacuum_reluctance(0.5*self.second_dimension_length,self.area_top)
            self.vacuum_reluctance_bottom = vacuum_reluctance(0.5*self.second_dimension_length,self.area_bottom)
            self.vacuum_reluctance_left = vacuum_reluctance(0.5*self.first_dimension_length, self.area_left)
            self.vacuum_reluctance_right = self.vacuum_reluctance_left

            self.length_top = 0.5*self.second_dimension_length
            self.length_bottom = self.length_top
            self.length_left = 0.5*self.first_dimension_length
            self.length_right = self.length_left
        
        # Các thuộc tính khởi tạo 1 lần, sử dụng nếu tối ưu vectorized
        self.area_top_invert = 1.0 / self.area_top
        self.area_right_invert = 1.0 / self.area_right
        self.area_bottom_invert = 1.0 / self.area_bottom
        self.area_left_invert = 1.0 / self.area_left

        self.area_radial_invert = 1.0 / (self.area_top + self.area_bottom)
        self.area_tangential_invert = 1.0 / (self.area_right + self.area_left)

        mu_g = self.material_database.air.relative_permeance
        mu_m = self.material_database.magnet.relative_permeance
        mu_r_max = find_maximum_permeance(self.material_database)

        if self.material == "air":
            mu_max = mu_g
        elif self.material == "magnet":
            mu_max = mu_m
        elif self.material == "iron":
            mu_max = mu_r_max
        else:
            mu_max = mu_g

        self.reluctance_minimum_top = self.vacuum_reluctance_top / mu_max
        self.reluctance_minimum_right = self.vacuum_reluctance_right / mu_max
        self.reluctance_minimum_bottom = self.vacuum_reluctance_bottom / mu_max
        self.reluctance_minimum_left = self.vacuum_reluctance_left / mu_max

    def update_from_flux_and_excitation(self, loop_flux_array, stator_excitation,update_reluctance = False, update_mmf_source = False):
        i, j = self.position
        if update_mmf_source == True:
            # Tỉ lệ element/segment
            element_ratio_first = self.first_dimension_length / self.segment_first_dimension_length
            element_ratio_second = self.second_dimension_length / self.segment_second_dimension_length

            # MMF cuộn dây
            winding_excitation_segment = float(matrix_product(stator_excitation, self.stator_excitation_coeffs))
            winding_excitation_second = winding_excitation_segment * self.cos_delta_angle_stator_excitation
            winding_excitation_first = winding_excitation_segment * self.sin_delta_angle_stator_excitation

            winding_excitation_top = winding_excitation_second * 0.5
            winding_excitation_bottom = winding_excitation_top
            winding_excitation_right = winding_excitation_first * 0.5 
            winding_excitation_left = winding_excitation_right

            # MMF nam châm
            magnetic_source_second = self.magnetic_source * np.cos(self.delta_angle_magnetic_source)
            magnetic_source_first = self.magnetic_source * np.sin(self.delta_angle_magnetic_source)

            self.magnet_source_top = magnetic_source_second * element_ratio_second * 0.5
            self.magnet_source_bottom = self.magnet_source_top
            self.magnet_source_right = magnetic_source_first * element_ratio_first * 0.5
            self.magnet_source_left = self.magnet_source_right

            # Tổng hợp 
            self.mmf_source_left = self.magnet_source_right + winding_excitation_right
            self.mmf_source_right = self.mmf_source_left
            self.mmf_source_top = self.magnet_source_top + winding_excitation_top
            self.mmf_source_bottom = self.mmf_source_top
        
        if update_reluctance == True:
            # Từ thông vòng (direct_flux) theo thứ tự: top/bottom = second_dimension, left/right = first_dimension
            self.direct_flux_top = float(-loop_flux_array.get_2D((i, j-1)) + loop_flux_array.get_2D((i, j)))
            self.direct_flux_bottom = float(-loop_flux_array.get_2D((i-1, j-1)) + loop_flux_array.get_2D((i-1, j)))
            self.direct_flux_left = float(-loop_flux_array.get_2D((i, j-1)) + loop_flux_array.get_2D((i-1, j-1)))
            self.direct_flux_right = float(-loop_flux_array.get_2D((i, j)) + loop_flux_array.get_2D((i-1, j)))

            # Mật độ từ thông
            self.flux_density_top = self.direct_flux_top / self.area_top
            self.flux_density_bottom = self.direct_flux_bottom / self.area_bottom
            self.flux_density_left = self.direct_flux_left / self.area_left
            self.flux_density_right = self.direct_flux_right / self.area_right


            # Mật độ trung bình
            self.flux_density_radial = (self.direct_flux_top + self.direct_flux_bottom)/(self.area_top + self.area_bottom)
            self.flux_density_tangential =-(self.direct_flux_left + self.direct_flux_right) / (self.area_right + self.area_left)
            self.average_flux_density = float(np.sqrt(self.flux_density_radial**2 + self.flux_density_tangential**2))

            # Từ trở phi tuyến 
            self.reluctance_top_value = self.reluctance_top()
            self.reluctance_bottom_value = self.reluctance_bottom()
            self.reluctance_left_value = self.reluctance_left()
            self.reluctance_right_value = self.reluctance_right()

    # --- Reluctance phi tuyến ---
    def reluctance_top(self):
        mu_0 = 4*pi*1e-7
        if self.material == "air":
            return [self.vacuum_reluctance_top, 0.0]
        elif self.material == "magnet":
            return [self.vacuum_reluctance_top/self.material_database.magnet.relative_permeance, 0.0]
        else:
            mu_r, dmu_r_dB = lookup_BH_curve(self.flux_density_top, self.material_database)
            R = self.vacuum_reluctance_top / mu_r
            dr_dphi = -(self.length_top/(mu_0*self.area_top)) * (1/mu_r**2) * dmu_r_dB * (1/self.area_top)
            return [R, dr_dphi]

    def reluctance_bottom(self):
        mu_0 = 4*pi*1e-7
        if self.material == "air":
            return [self.vacuum_reluctance_bottom, 0.0]
        elif self.material == "magnet":
            return [self.vacuum_reluctance_bottom/self.material_database.magnet.relative_permeance, 0.0]
        else:
            mu_r, dmu_r_dB = lookup_BH_curve(self.flux_density_bottom, self.material_database)
            R = self.vacuum_reluctance_bottom / mu_r
            dr_dphi = -(self.length_bottom/(mu_0*self.area_bottom)) * (1/mu_r**2) * dmu_r_dB * (1/self.area_bottom)
            return [R, dr_dphi]

    def reluctance_left(self):
        mu_0 = 4*pi*1e-7
        if self.material == "air":
            return [self.vacuum_reluctance_left, 0.0]
        elif self.material == "magnet":
            return [self.vacuum_reluctance_left/self.material_database.magnet.relative_permeance, 0.0]
        else:
            mu_r, dmu_r_dB = lookup_BH_curve(self.flux_density_left, self.material_database)
            R = self.vacuum_reluctance_left / mu_r
            dr_dphi = -(self.length_left/(mu_0*self.area_left)) * (1/mu_r**2) * dmu_r_dB * (1/self.area_left)
            return [R, dr_dphi]

    def reluctance_right(self):
        mu_0 = 4*pi*1e-7
        if self.material == "air":
            return [self.vacuum_reluctance_right, 0.0]
        elif self.material == "magnet":
            return [self.vacuum_reluctance_right/self.material_database.magnet.relative_permeance, 0.0]
        else:
            mu_r, dmu_r_dB = lookup_BH_curve(self.flux_density_right, self.material_database)
            R = self.vacuum_reluctance_right / mu_r
            dr_dphi = -(self.length_right/(mu_0*self.area_right)) * (1/mu_r**2) * dmu_r_dB * (1/self.area_right)
            return [R, dr_dphi]
        
    def coenergy(self):
        """
        Tính toán co-energy (phiên bản đã vector hóa).
        """
        
        # --- Nhánh ELSE (tuyến tính) ---
        # Nhánh này đã nhanh, xử lý trước và return sớm
        if self.material != "iron":
            coenergy = (self.reluctance_top_value[0] * (self.direct_flux_top**2))/2
            coenergy += (self.reluctance_right_value[0] * (self.direct_flux_right**2))/2
            coenergy += (self.reluctance_bottom_value[0] * (self.direct_flux_bottom**2))/2
            coenergy += (self.reluctance_left_value[0] * (self.direct_flux_left**2))/2
            return coenergy

        # --- Nhánh IF "iron" (phi tuyến) ---
        resolution = 20
        
        # 1. Gom tất cả dữ liệu của 4 nhánh vào các mảng NumPy (shape: (4,))
        # Chúng ta dùng np.asarray và abs() MỘT LẦN DUY NHẤT
        fluxes = np.abs(np.asarray([
            self.direct_flux_top,
            self.direct_flux_right,
            self.direct_flux_bottom,
            self.direct_flux_left
        ], dtype=float))
        
        areas = np.asarray([
            self.area_top,
            self.area_right,
            self.area_bottom,
            self.area_left
        ], dtype=float)
        
        vac_reluctances = np.asarray([
            self.vacuum_reluctance_top,
            self.vacuum_reluctance_right,
            self.vacuum_reluctance_bottom,
            self.vacuum_reluctance_left
        ], dtype=float)

        # 2. Tạo ma trận Phi (shape: (4, 8))
        # Tính np.linspace cho cả 4 nhánh cùng lúc
        start_points = np.zeros(4)
        # axis=1 nghĩa là linspace được thực hiện theo hàng ngang
        Phi_matrix = np.linspace(start_points, fluxes, resolution, axis=1)
        
        # 3. Tính delta_phi cho mỗi nhánh (shape: (4,))
        delta_phi = Phi_matrix[:, 1] - Phi_matrix[:, 0]

        # 4. Tính ma trận B (shape: (4, 8))
        # Dùng NumPy broadcasting (chia ma trận (4, 8) cho vector (4, 1))
        B_matrix = Phi_matrix / areas[:, np.newaxis]

        # 5. Tính ma trận mu (shape: (4, 8))
        # Đây là bước quan trọng: gọi hàm lookup_BH_curve MỘT LẦN
        # với toàn bộ ma trận B.
        mu_matrix, _ = lookup_BH_curve(
            B_matrix, 
            self.material_database, 
            return_du_dB=False
        )
        
        # 6. Tính ma trận Reluctance (shape: (4, 8))
        # Lại dùng broadcasting
        R_matrix = vac_reluctances[:, np.newaxis] / mu_matrix
        
        # 7. Tính tích phân co-energy
        # (delta_phi * R * phi) cho mỗi phần tử
        integrand_matrix = R_matrix * Phi_matrix
        
        # Tính tổng của tích phân cho mỗi nhánh (tổng theo axis 1)
        # Kết quả là mảng (4,)
        sum_per_branch = np.sum(integrand_matrix, axis=1)
        
        # Nhân với delta_phi của từng nhánh
        coenergy_per_branch = delta_phi * sum_per_branch
        
        # 8. Tính tổng co-energy cuối cùng
        total_coenergy = np.sum(coenergy_per_branch)

        return float(total_coenergy)

    def display(self, ax=None, show_label=False, interactive=True, linewidth=0.0):
        """
        Vẽ element này trên ax.
        - show_label: hiện (i,j) hoặc material ở giữa element.
        - interactive: bật picker trên patch (mặc định True).
        Trả về ax và lưu patch vào self._patch; gắn poly._element_ref = self để ReluctanceNetwork bắt event.
        """
        # đảm bảo figure/axes
        if ax is None:
            fig, ax = plt.subplots(figsize=(6, 6))
        else:
            fig = ax.figure

        coords_first, coords_second = self.grid.grid_coordinate
        gtype = self.grid.type
        i, j = self.position

        # --- Tạo điểm polygon tùy loại grid ---
        if gtype == "polar":
            theta_array, r_array = coords_first, coords_second
            r_in = float(r_array[i])
            r_out = float(r_array[i + 1])
            theta1 = float(theta_array[j])
            theta2 = float(theta_array[j + 1])

            points = [
                (r_in * np.cos(theta1), r_in * np.sin(theta1)),
                (r_out * np.cos(theta1), r_out * np.sin(theta1)),
                (r_out * np.cos(theta2), r_out * np.sin(theta2)),
                (r_in * np.cos(theta2), r_in * np.sin(theta2)),
            ]
            mid_r = 0.5 * (r_in + r_out)
            mid_theta = 0.5 * (theta1 + theta2)
            cx = mid_r * np.cos(mid_theta)
            cy = mid_r * np.sin(mid_theta)

        elif gtype == "cartesian":
            x_array, y_array = coords_first, coords_second
            x0 = float(x_array[j])
            x1 = float(x_array[j + 1])
            y0 = float(y_array[i])
            y1 = float(y_array[i + 1])

            points = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
            cx = 0.5 * (x0 + x1)
            cy = 0.5 * (y0 + y1)

        elif gtype == "trapezoid":
            theta_array, r_array = coords_first, coords_second
            r_in = float(r_array[i])
            r_out = float(r_array[i + 1])
            theta1 = float(theta_array[j])
            theta2 = float(theta_array[j + 1])

            points = [
                (r_in * np.cos(theta1), r_in * np.sin(theta1)),
                (r_in * np.cos(theta2), r_in * np.sin(theta2)),
                (r_out * np.cos(theta2), r_out * np.sin(theta2)),
                (r_out * np.cos(theta1), r_out * np.sin(theta1)),
            ]
            mid_r = 0.5 * (r_in + r_out)
            mid_theta = 0.5 * (theta1 + theta2)
            cx = mid_r * np.cos(mid_theta)
            cy = mid_r * np.sin(mid_theta)

        else:
            raise ValueError(f"Unsupported grid type: {gtype}")

        # --- Màu theo material (giữ như trước) ---
        facecolor = None
        if isinstance(self.material, str):
            if self.material == "air":
                facecolor = "none"
                alpha = 1.0
            elif self.material == "iron":
                facecolor = "#A3A3A3"
                #facecolor = "#000000"
                alpha = 1.0
            elif self.material == "magnet":
                delta = getattr(self, "delta_angle_magnetic_source", 0)
                facecolor = "#CC0000" if delta >= 0 else "#0033CC"
                #facecolor = "#000000"
                alpha = 1.0
            else:
                facecolor = "white"
                alpha = 1.0
        else:
            facecolor = getattr(self.material, "color", "white")
            alpha = 1.0

        # --- Tạo patch, bật picker theo interactive ---
        poly = MplPolygon(
            points,
            closed=True,
            facecolor=facecolor,
            edgecolor="gray",
            linewidth=linewidth,
            alpha=alpha,
            picker=interactive,
        )
        ax.add_patch(poly)

        # lưu tham chiếu patch và gắn reference để handler bắt được
        self._patch = poly
        poly._element_ref = self

        # Hiển thị label tĩnh nếu cần
        if show_label:
            label = getattr(self, "index", getattr(self, "material", ""))
            # lưu text object để có thể xóa sau này nếu cần
            try:
                self._label_text = ax.text(cx, cy, f"{label}", ha="center", va="center", fontsize=6)
            except Exception:
                self._label_text = None
            self._label_text_visible = True
        else:
            self._label_text_visible = False
            self._label_text = None

        ax.set_aspect("equal")
        ax.autoscale()

        return ax
