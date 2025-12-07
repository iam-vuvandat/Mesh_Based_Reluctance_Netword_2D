import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon
from matplotlib.colors import LinearSegmentedColormap
from motor_geometry.models.Element import Element
from material_data.models.MaterialDataBase import MaterialDataBase
from material_data.utils.find_maximum_permeance import find_maximum_permeance
from solver.utils.create_loop_flux_array import create_loop_flux_array
from solver.utils.create_line_array import create_line_array
from motor_geometry.models.VectorizedElement import VectorizedElement
import math
from motor_geometry.utils.compute_segment_grid_dimensions import compute_segment_grid_dimensions
pi = math.pi

class ReluctanceNetwork:
    def __init__(self, segments, grid, loop_flux_array=None, stator_excitation=None,cyclic_type="no_cyclic",optimization = "vectorized"):
        
        self.segments = segments 
        self.grid = grid
        self.optimization = optimization
        self.material_database = MaterialDataBase()
        self.theta_resolution = grid.delta_theta
        self.rotor_position = 0.0

        for segment in segments:
            compute_segment_grid_dimensions(segment,self.grid)

        self.cyclic_type = cyclic_type
        self.size = self.grid.size

        if loop_flux_array is None:
            loop_flux_array = create_loop_flux_array(self)

        if stator_excitation is None:
            self.phase_number = segments[0].stator_excitation_coeffs.size
            stator_excitation = create_line_array([],self.phase_number)

        self._loop_flux_array = loop_flux_array
        self._stator_excitation = stator_excitation
        self._create_elements()

        if self.optimization == "vectorized":
            self.vectorized_element = VectorizedElement(reluctance_network=self)
            self.vectorized_element.update_reluctance(self)
            self.vectorized_element.update_mmf_source(self)

    def _create_elements(self):
        number_of_row = int(self.size[0])
        number_of_col = int(self.size[1])
        self.elements = []
        for i in range(number_of_row):
            for j in range(number_of_col):
                position = (i, j)
                element = Element(
                    position=position,
                    segments=self.segments,
                    grid = self.grid,
                    loop_flux_array=self._loop_flux_array,
                    stator_excitation=self._stator_excitation
                )
                self.elements.append(element)

    @property
    def loop_flux_array(self):
        return self._loop_flux_array

    @loop_flux_array.setter
    def loop_flux_array(self, new_flux_array):
        self._loop_flux_array = new_flux_array
        if self.optimization == "standard":
            self._update_all_elements(update_reluctance = True)
        elif self.optimization == "vectorized":
            self.vectorized_element.update_reluctance(self)

    @property
    def stator_excitation(self):
        return self._stator_excitation

    @stator_excitation.setter
    def stator_excitation(self, new_excitation):
        self._stator_excitation = new_excitation
        if self.optimization == "standard":
            self._update_all_elements(update_mmf_source = True)
        elif self.optimization == "vectorized":
            self.vectorized_element.update_mmf_source(self)

    def _update_all_elements(self, update_reluctance = False, update_mmf_source = False):
        """Cập nhật toàn bộ element với flux/excitation mới"""
        for elem in self.elements:
            elem.update_from_flux_and_excitation(self._loop_flux_array, self._stator_excitation, update_reluctance , update_mmf_source)

    def get_element(self, position):
        """
        Trả về một Element ở vị trí position(i,j), xử lý tính chất tuần hoàn
        """
        if not isinstance(position, tuple) or len(position) != 2:
            raise TypeError("get_element cần truyền vào tuple có dạng (i, j)")

        i, j = position
        n_rows  = int(self.size[0])
        n_cols = int(self.size[1])
        
        # Xử lý chỉ sổ trong trường hợp lưới không tuần hoàn
        if self.cyclic_type =="no_cyclic": 
            if i<0 or i>= n_rows:
                return None
            elif j<0 or j>= n_cols:
                return None
            else:
               return self.elements[(i * n_cols )+ j]

        # Lưới tuần hoàn theo hướng first_dimension:
        elif self.cyclic_type =="first_dimension":
            if i<0 or i>= n_rows:
                return None
            else:
                j = j % n_cols
                return self.elements[(i * n_cols )+ j]

        # Lưới tuần hoàn theo second_dimension       
        elif self.cyclic_type =="second_dimension":
            if j<0 or j>= n_cols:
                return None
            else:
                i = i % n_rows
                return self.elements[(i * n_cols )+ j]

        # Lưới tuần hoàn theo cả 2 hướng 
        elif self.cyclic_type == "both":
            i = i % n_rows
            j = j % n_cols
            return self.elements[(i * n_cols )+ j]

        
    def __getitem__(self, position):
        """
        Cho phép truy cập trực tiếp rn[i, j] thay vì rn.get_element((i, j)).
        Chỉ chấp nhận tuple.
        """
        if not isinstance(position, tuple) or len(position) != 2:
            raise TypeError("Index phải là tuple (i, j)")

        return self.get_element(position)
    
    def set_iron_reluctance_minimum(self):
        
        """
        Trong bước đầu tiên của Newton-Rapshon, ta cần một điểm khởi đầu đủ tốt
        Nếu không ngiệm sẽ không hội tụ.
        Chọn các từ trở sắt đạt giá trị cực tiểu, tức độ từ thẩm cực đại
        ( tức đạo hàm =0), khi đó bước đầu tiên của Newton-Rapshon chắc chắn sẽ tiến đến nghiệm 
        -> Khởi đầu bền vững
        """
        # tìm độ từ thẩm sắt cực đại
        material_database = MaterialDataBase()
        maximum_permeance = find_maximum_permeance(material_database)

        # Truy cập vào các Element sắt, cài độ từ thẩm sắt cực tiểu
        
        for element in self.elements:
            if element.material == "iron":
                element.reluctance_top_value = [element.vacuum_reluctance_top / maximum_permeance,0.0]
                element.reluctance_right_value = [element.vacuum_reluctance_right / maximum_permeance,0.0]
                element.reluctance_bottom_value = [element.vacuum_reluctance_bottom / maximum_permeance,0.0]     
                element.reluctance_left_value = [element.vacuum_reluctance_left / maximum_permeance,0.0]

    def coenergy(self,enable = False):
        coenergy = 0.0
        if enable == True:
            number_of_rows, number_of_cols = self.size 
            for i in range(number_of_rows):
                for j in range(number_of_cols):
                    # Cộng coenergy 4 hướng: 
                    eij = self.get_element((i,j))
                    coenergy += eij.coenergy()
        return coenergy

    def shift_element(self, ring_shift, direction):
        """
        Xoay mạng từ trở bằng cách dịch chuyển các element theo quy luật sau:
        - direction > 0: dịch sang phải / xuống (tùy cyclic_type)
        - direction < 0: dịch sang trái / lên
        - cyclic_type:
            + "first_dimension": dịch chuyển các phần tử theo cột (theo j)
            + "second_dimension": dịch chuyển các phần tử theo hàng (theo i)
        - ring_shift: tuple (begin, end): chỉ các hàng hoặc cột trong khoảng này mới bị xoay
        """
        if self.optimization =="standard":
            number_of_rows, number_of_cols = self.size
            ring_begin, ring_end = ring_shift

            if self.cyclic_type == "first_dimension":
                self.rotor_position = self.rotor_position +( self.theta_resolution * direction)
                # Dịch chuyển theo chiều ngang (các cột trong từng hàng)
                for i in range(ring_begin, ring_end + 1):
                    # lấy các element trong hàng i
                    row_elems = [self.get_element((i, j)) for j in range(number_of_cols)]
                    # xoay list theo direction
                    direction_mod = direction % number_of_cols
                    new_row = row_elems[-direction_mod:] + row_elems[:-direction_mod]
                    # gán lại element và cập nhật position
                    for j, elem in enumerate(new_row):
                        idx = i * number_of_cols + j
                        self.elements[idx] = elem
                        elem.position = (i, j)

            elif self.cyclic_type == "second_dimension":
                # Dịch chuyển theo chiều dọc (các hàng trong từng cột)
                for j in range(ring_begin, ring_end + 1):
                    # lấy các element trong cột j
                    col_elems = [self.get_element((i, j)) for i in range(number_of_rows)]
                    # xoay list theo direction
                    direction_mod = direction % number_of_rows
                    new_col = col_elems[-direction_mod:] + col_elems[:-direction_mod]
                    # gán lại element và cập nhật position
                    for i, elem in enumerate(new_col):
                        idx = i * number_of_cols + j
                        self.elements[idx] = elem
                        elem.position = (i, j)

            else:
                raise ValueError(f"shift_element chỉ hỗ trợ cyclic_type=first_dimension hoặc second_dimension, "
                                f"nhưng đang là {self.cyclic_type}")
        elif self.optimization == "vectorized":
            self.vectorized_element.shift(ring_shift=ring_shift,direction=direction)

    def export_flux_density(self,slice_type = "row", position = 0 ):
        if self.optimization == "vectorized":
            return self.vectorized_element.export_flux_density(slice_type=slice_type,position=position)
        elif self.optimization == "standard":
            if slice_type == "row":
                col_number = self.size[1]
                flux_density = np.zeros((4,col_number))
                for i in range(col_number):
                    flux_density[0,i] = self.get_element((position,i)).average_flux_density
                    flux_density[1,i] = self.get_element((position,i)).flux_density_radial
                    flux_density[2,i] = self.get_element((position,i)).flux_density_tangential
                    flux_density[3,i] = self.theta_resolution * i 
                return flux_density

    def flux_linkage(self):
        if self.optimization == "standard":
            flux_linkage = create_line_array([],self.phase_number)
            for element in self.elements:
                    radial_flux =  float(element.direct_flux_top + element.direct_flux_bottom) / 2
                    winding_excitation_coeffs = element.stator_excitation_coeffs
                    for k in range(self.phase_number):
                        flux_linkage[k] += radial_flux * float(winding_excitation_coeffs[k])
            return flux_linkage
        
        elif self.optimization == "vectorized":
            return self.vectorized_element.flux_linkage()
        
    
    def maxwell_stress_tensor(self,ring):
        if self.optimization == "standard":
            mu_0 = 4* pi * 1e-7
            number_of_col = int(self.size[1])
            torque_maxwell_stress_tensor = 0.0
            for i in range(number_of_col):
                element = self.get_element((ring,i))
                r = (element.inner_second_dimension + element.outer_second_dimension)/2
                theta = element.open_angle
                l = element.axial_length
                B_r = element.flux_density_radial
                B_t = element.flux_density_tangential
                torque_maxwell_stress_tensor -= (l*r*r/mu_0) * B_r * B_t * theta

            return torque_maxwell_stress_tensor
        elif self.optimization == "vectorized":
            return self.vectorized_element.torque_maxwell_stress_tensor(ring)

    

    def view_flux_density(self, ax=None, show_colorbar=True, show_segment_edges=False,
                        vmin=0.0, vmax=2.0, fit_mode="square", show_plot=False,show_full = True):
        """
        Vẽ bản đồ mật độ từ thông B trên toàn bộ lưới.
        Nếu lưới thuộc loại 'polar' hoặc 'trapezoid', mặc định sẽ nhân bản hình theo chu kỳ 2π.
        Tự động căn lề 10% để tránh đồ thị bị sát mép.
        """

        # ======================================================
        # CẬP NHẬT (cho chế độ vectorized)
        # ======================================================
        if self.optimization == "vectorized":
            self._update_all_elements(update_reluctance=True, update_mmf_source=True)

        if ax is None:
            fig, ax = plt.subplots(figsize=(12, 12))
        else:
            fig = ax.figure

        # ======================================================
        # THU THẬP DỮ LIỆU CƠ BẢN
        # ======================================================
        B_vals = np.array([elem.average_flux_density for elem in self.elements])
        norm = plt.Normalize(vmin=vmin, vmax=vmax)

        # ====== THAY COLORMAP BẰNG BẢNG MÀU BẠN CUNG CẤP ======
        from matplotlib.colors import LinearSegmentedColormap

        colors_hex = [
            "#0000ff", "#0049ff", "#0092ff", "#00dbff",
            "#00ffdb", "#00ff92", "#00ff49", "#00ff00",
            "#49ff00", "#92ff00", "#dbff00", "#ffdb00",
            "#ff9200", "#ff4900", "#ff0000"
        ]
        
        colormap = LinearSegmentedColormap.from_list("custom_fluxmap", colors_hex, N=256)

        coords_first, coords_second = self.grid.grid_coordinate
        gtype = self.grid.type

        # ======================================================
        # XÁC ĐỊNH SỐ LẦN NHÂN BẢN
        # ======================================================
        if gtype in ("polar", "trapezoid"):
            theta_start, theta_end = float(coords_first[0]), float(coords_first[-1])
            dtheta = abs(theta_end - theta_start)
            repeat_count = max(1, int(round(2 * np.pi / dtheta)))
            if show_full == False:
                repeat_count = 1
        else:
            repeat_count = 1

        # ======================================================
        # HÀM VẼ MỘT SECTOR
        # ======================================================
        def _draw_sector(theta_shift=0.0):
            for elem, B in zip(self.elements, B_vals):
                i, j = elem.position

                if gtype == "polar":
                    theta_array, r_array = coords_first, coords_second
                    r_in = float(r_array[i])
                    r_out = float(r_array[i+1])
                    theta1 = float(theta_array[j]) + theta_shift
                    theta2 = float(theta_array[j+1]) + theta_shift
                    points = [
                        (r_in * np.cos(theta1),  r_in * np.sin(theta1)),
                        (r_out * np.cos(theta1), r_out * np.sin(theta1)),
                        (r_out * np.cos(theta2), r_out * np.sin(theta2)),
                        (r_in * np.cos(theta2),  r_in * np.sin(theta2))
                    ]

                elif gtype == "trapezoid":
                    theta_array, r_array = coords_first, coords_second
                    r_in = float(r_array[i])
                    r_out = float(r_array[i+1])
                    theta1 = float(theta_array[j]) + theta_shift
                    theta2 = float(theta_array[j+1]) + theta_shift
                    points = [
                        (r_in * np.cos(theta1),  r_in * np.sin(theta1)),
                        (r_in * np.cos(theta2),  r_in * np.sin(theta2)),
                        (r_out * np.cos(theta2), r_out * np.sin(theta2)),
                        (r_out * np.cos(theta1), r_out * np.sin(theta1))
                    ]

                elif gtype == "cartesian":
                    x_array, y_array = coords_first, coords_second
                    x0, x1 = float(x_array[j]), float(x_array[j+1])
                    y0, y1 = float(y_array[i]), float(y_array[i+1])
                    points = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]

                else:
                    raise ValueError(f"Unsupported grid type: {gtype}")

                poly = MplPolygon(
                    points,
                    closed=True,
                    facecolor=colormap(norm(B)),
                    edgecolor="none",
                    linewidth=0.0
                )
                ax.add_patch(poly)

        # ======================================================
        # VẼ TẤT CẢ SECTOR
        # ======================================================
        if repeat_count == 1:
            _draw_sector()
        else:
            for k in range(repeat_count):
                theta_shift = k * (2 * np.pi / repeat_count)
                _draw_sector(theta_shift)

        # ======================================================
        # VẼ VIỀN SEGMENT (NẾU CÓ)
        # ======================================================
        if show_segment_edges:
            for segment in self.segments:
                if segment.polygon is not None:
                    x, y = segment.polygon.exterior.xy
                    coords = np.column_stack((x, y))
                    seg_patch = MplPolygon(
                        coords,
                        closed=True,
                        facecolor='none',
                        edgecolor='white',
                        linewidth=0.2
                    )
                    ax.add_patch(seg_patch)

        ax.set_aspect("equal")

        # ======================================================
        # CĂN LỀ + FIT
        # ======================================================
        all_x, all_y = [], []
        for patch in ax.patches:
            xy = patch.get_xy()
            all_x.extend(xy[:,0])
            all_y.extend(xy[:,1])

        if all_x and all_y:
            min_x, max_x = min(all_x), max(all_x)
            min_y, max_y = min(all_y), max(all_y)
            width = max_x - min_x
            height = max_y - min_y

            if fit_mode == "tight":
                ax.set_xlim(min_x - 0.1*width,  max_x + 0.1*width)
                ax.set_ylim(min_y - 0.1*height, max_y + 0.1*height)

            elif fit_mode == "square":
                cx = (min_x + max_x) / 2
                cy = (min_y + max_y) / 2
                half_range = max(width, height) * 0.55
                ax.set_xlim(cx - half_range, cx + half_range)
                ax.set_ylim(cy - half_range, cy + half_range)

        ax.set_xlabel("X (m)")
        ax.set_ylabel("Y (m)")
        ax.set_title("Flux Density (T)")

        # ======================================================
        # COLORBAR
        # ======================================================
        if show_colorbar:
            sm = plt.cm.ScalarMappable(cmap=colormap, norm=norm)
            sm.set_array([])
            fig.colorbar(sm, ax=ax, label="Flux density B (T)")

        if show_plot:
            plt.show()

        return ax

    
    def display(self, ax=None, show_label=False, interactive=True, show_segment_edges=False):
        """
        Vẽ toàn bộ mạng từ trở.
        - show_label: hiện label (index/material) ở giữa mỗi element (tĩnh).
        - interactive: khi True, bật khả năng click (pick) để in thông tin và hiển thị annotation trên plot.
                    (Mặc định True)
        - show_segment_edges: vẽ viền segment (hình học gốc).
        """
        
        if self.optimization == "vectorized":
            self._update_all_elements(update_reluctance=True, update_mmf_source=True)

        if ax is None:
            fig, ax = plt.subplots(figsize=(12, 12))
        else:
            fig = ax.figure

        # vẽ grid nếu có method display
        try:
            if hasattr(self, "grid") and hasattr(self.grid, "display"):
                self.grid.display(ax=ax)
        except Exception:
            pass

        # Vẽ tất cả element (bật picker trên từng element)
        for elem in self.elements:
            try:
                elem.display(ax=ax, show_label=show_label, interactive=interactive)
            except Exception:
                continue
            try:
                elem._label_text_visible = False
            except Exception:
                elem._label_text_visible = False

        current_label = {"text": None, "ref": None}

        def _fmt(x, fmt_str="{:.6g}"):
            try:
                if x is None:
                    return "None"
                if isinstance(x, (int, float)):
                    return fmt_str.format(x)
                return str(x)
            except Exception:
                return str(x)

        def on_pick(event):
            artist = getattr(event, "artist", None)
            if artist is None:
                return

            elem = getattr(artist, "_element_ref", None)
            seg = getattr(artist, "_segment_ref", None)
            ref = elem if elem is not None else seg
            if ref is None:
                return

            if current_label["text"] is not None:
                try:
                    current_label["text"].remove()
                except Exception:
                    pass
                current_label["text"] = None

            if getattr(ref, "_label_text_visible", False):
                ref._label_text_visible = False
                try:
                    current_label["ref"] = None
                except Exception:
                    pass
                fig.canvas.draw_idle()
                return

            info_lines = []
            cx = None
            cy = None

            if elem is not None:
                try:
                    xy = artist.get_xy()
                    cx = float(xy[:, 0].mean())
                    cy = float(xy[:, 1].mean())
                except Exception:
                    try:
                        coords_first, coords_second = elem.grid.grid_coordinate
                        if elem.grid.type == "cartesian":
                            x_array, y_array = coords_first, coords_second
                            x0 = float(x_array[elem.position[1]])
                            x1 = float(x_array[elem.position[1] + 1])
                            y0 = float(y_array[elem.position[0]])
                            y1 = float(y_array[elem.position[0] + 1])
                            cx = 0.5 * (x0 + x1)
                            cy = 0.5 * (y0 + y1)
                        else:
                            cx, cy = 0.0, 0.0
                    except Exception:
                        cx, cy = 0.0, 0.0

                info_lines.append(f"Element {getattr(elem, 'position', None)}")
                info_lines.append(f"  material: {getattr(elem, 'material', None)}")
                info_lines.append(f"  index: {getattr(elem, 'index', None)}")
                info_lines.append(f"  avg B: { _fmt(getattr(elem, 'average_flux_density', None), '{:.6g}') } T")
                info_lines.append(f"  mmf L/R: {_fmt(getattr(elem, 'mmf_source_left', None))} / {_fmt(getattr(elem, 'mmf_source_right', None))}")
                info_lines.append(f"  mmf T/B: {_fmt(getattr(elem, 'mmf_source_top', None))} / {_fmt(getattr(elem, 'mmf_source_bottom', None))}")
                info_lines.append(f"  direct_flux (T,R,B,L): {_fmt(getattr(elem, 'direct_flux_top', None))}, {_fmt(getattr(elem, 'direct_flux_right', None))}, {_fmt(getattr(elem, 'direct_flux_bottom', None))}, {_fmt(getattr(elem, 'direct_flux_left', None))}")
                info_lines.append("  reluctances (R, dR/dphi):")
                info_lines.append(f"    top: {getattr(elem, 'reluctance_top_value', None)}")
                info_lines.append(f"    bottom: {getattr(elem, 'reluctance_bottom_value', None)}")
                info_lines.append(f"    left: {getattr(elem, 'reluctance_left_value', None)}")
                info_lines.append(f"    right: {getattr(elem, 'reluctance_right_value', None)}")
                info_lines.append(f"  stator_coeffs: {_fmt(getattr(elem, 'stator_excitation_coeffs', None))}")

            else:
                try:
                    cx = float(seg.polygon.centroid.x)
                    cy = float(seg.polygon.centroid.y)
                except Exception:
                    try:
                        xy = artist.get_xy()
                        cx = float(xy[:, 0].mean())
                        cy = float(xy[:, 1].mean())
                    except Exception:
                        cx, cy = 0.0, 0.0

                info_lines.append(f"Segment")
                info_lines.append(f"  material: {getattr(seg, 'material', None)}")
                info_lines.append(f"  index: {getattr(seg, 'index', None)}")
                info_lines.append(f"  axial_length: {_fmt(getattr(seg, 'axial_length', None))}")
                info_lines.append(f"  magnetic_source: {_fmt(getattr(seg, 'magnetic_source', None))}")
                info_lines.append(f"  Δangle_magnetic_source: {_fmt(getattr(seg, 'delta_angle_magnetic_source', None))} rad")
                info_lines.append(f"  Δangle_stator_excitation: {_fmt(getattr(seg, 'delta_angle_stator_excitation', None))} rad")
                info_lines.append(f"stator_excitation_coeffs: {_fmt(getattr(elem, 'stator_excitation_coeffs', None))}")
                try:
                    info_lines.append(f"  segment_first_dimension_length: {_fmt(getattr(seg, 'segment_first_dimension_length', None))}")
                except Exception:
                    pass

            info_text = "\n".join(info_lines)

            try:
                text = ax.text(
                    cx, cy, info_text,
                    fontsize=8, ha='center', va='center', color='black',
                    bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5')
                )
                current_label["text"] = text
                current_label["ref"] = ref
                ref._label_text_visible = True
            except Exception:
                print(info_text)
                current_label["text"] = None
                current_label["ref"] = ref
                ref._label_text_visible = True

            fig.canvas.draw_idle()

        try:
            if hasattr(self, "_pick_cid") and getattr(self, "_pick_cid") is not None:
                try:
                    fig.canvas.mpl_disconnect(self._pick_cid)
                except Exception:
                    pass
        except Exception:
            pass

        if interactive:
            self._pick_cid = fig.canvas.mpl_connect("pick_event", on_pick)
        else:
            self._pick_cid = None

        if show_segment_edges:
            for segment in self.segments:
                try:
                    if segment.polygon is not None:
                        x, y = segment.polygon.exterior.xy
                        coords = np.column_stack((x, y))
                        seg_patch = MplPolygon(
                            coords,
                            closed=True,
                            facecolor='none',
                            edgecolor='black',
                            linewidth=1.0
                        )
                        ax.add_patch(seg_patch)
                except Exception:
                    continue

        ax.set_aspect("equal")
        ax.autoscale()

        all_x, all_y = [], []
        try:
            for patch in ax.patches:
                if isinstance(patch, MplPolygon):
                    xy = patch.get_xy()
                    all_x.extend(xy[:, 0])
                    all_y.extend(xy[:, 1])
        except Exception:
            pass

        if all_x and all_y:
            try:
                min_x, max_x = min(all_x), max(all_x)
                min_y, max_y = min(all_y), max(all_y)

                width = max_x - min_x
                height = max_y - min_y

                cx = 0.5 * (min_x + max_x)
                cy = 0.5 * (min_y + max_y)

                half_range = max(width, height) / 2

                # === Thêm margin 10% ở đây ===
                margin = 0.10
                half_range *= (1 + margin)
                # ==============================

                ax.set_xlim(cx - half_range, cx + half_range)
                ax.set_ylim(cy - half_range, cy + half_range)
            except Exception:
                pass

        ax.set_xlabel("X (m)")
        ax.set_ylabel("Y (m)")
        plt.show()
        return ax


        
        
       



