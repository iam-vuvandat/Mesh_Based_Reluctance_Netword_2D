from collections import defaultdict
import numpy as np
from shapely.geometry import Polygon
import warnings

def extract_element_info(position, Grid, segments):
    """
    Trích xuất thông tin đầy đủ cho Element tại vị trí position (i,j).
    Trả về **15** trường (theo thứ tự):
      1. material
      2. index
      3. axial_length
      4. magnetic_source
      5. delta_angle_magnetic_source
      6. stator_excitation_coeffs (np.array)
      7. delta_angle_stator_excitation
      8. segment_first_dimension_length   (từ segment nếu có, ngược lại fallback)
      9. segment_opening_angle            (từ segment nếu có)
     10. segment_second_dimension_length (từ segment nếu có)
     11. inner_first_dimension           (tính từ grid)
     12. outer_first_dimension           (tính từ grid)
     13. first_dimension_length          (tính từ grid)
     14. open_angle                      (tính từ grid)
     15. second_dimension_length         (tính từ grid)
    """

    # kiểm tra position
    if not isinstance(position, tuple) or len(position) != 2:
        raise TypeError("position phải là tuple có dạng (i, j)")

    eps = 1e-12

    # xác định số pha: 
    phase_number = segments[0].stator_excitation_coeffs.size



    # --- Tính các kích thước theo Grid (grid-level geometry) và tạo element polygon ---
    if Grid.type == "polar" or Grid.type == "trapezoid":
        theta_grid, r_grid = Grid.grid_coordinate
        i_r, i_theta = position

        if i_r < 0 or i_r + 1 >= len(r_grid):
            raise IndexError(f"i_r out of range: {i_r}, len(r_grid)={len(r_grid)}")
        if i_theta < 0 or i_theta + 1 >= len(theta_grid):
            raise IndexError(f"i_theta out of range: {i_theta}, len(theta_grid)={len(theta_grid)}")

        r_inner = float(r_grid[i_r])
        r_outer = float(r_grid[i_r + 1])
        theta_start = float(theta_grid[i_theta])
        theta_end   = float(theta_grid[i_theta + 1])

        d_r = abs(r_outer - r_inner)
        if d_r <= eps:
            diffs = np.diff(np.asarray(r_grid, dtype=float))
            positive = diffs[diffs > eps]
            d_r = float(positive.min()) if positive.size > 0 else eps

        d_theta = abs(theta_end - theta_start)
        if d_theta <= eps:
            diffs_t = np.diff(np.asarray(theta_grid, dtype=float))
            positive_t = diffs_t[diffs_t > eps]
            d_theta = float(positive_t.min()) if positive_t.size > 0 else eps

        # grid-level values
        inner_first_dimension = r_inner
        outer_first_dimension = r_outer
        open_angle = d_theta

        if Grid.type == "polar":
            r_avg = 0.5 * (r_inner + r_outer)
            first_dimension_length = r_avg * d_theta           # xấp xỉ cung tròn
            second_dimension_length = d_r
        else:  # trapezoid
            # công thức chính xác cho hình thang cân
            arc_inner = 2 * r_inner * np.sin(d_theta/2.0)
            arc_outer = 2 * r_outer * np.sin(d_theta/2.0)
            first_dimension_length = 0.5 * (arc_inner + arc_outer)
            second_dimension_length = r_outer - r_inner

        element_polygon = Polygon([
            (r_inner * np.cos(theta_start), r_inner * np.sin(theta_start)),
            (r_outer * np.cos(theta_start), r_outer * np.sin(theta_start)),
            (r_outer * np.cos(theta_end),   r_outer * np.sin(theta_end)),
            (r_inner * np.cos(theta_end),   r_inner * np.sin(theta_end)),
        ])

    elif Grid.type == "cartesian":
        x_grid, y_grid = Grid.grid_coordinate
        i_y, i_x = position

        if i_x < 0 or i_x + 1 >= len(x_grid):
            raise IndexError(f"i_x out of range: {i_x}, len(x_grid)={len(x_grid)}")
        if i_y < 0 or i_y + 1 >= len(y_grid):
            raise IndexError(f"i_y out of range: {i_y}, len(y_grid)={len(y_grid)}")

        x_low  = float(x_grid[i_x])
        x_high = float(x_grid[i_x + 1])
        y_low  = float(y_grid[i_y])
        y_high = float(y_grid[i_y + 1])

        dx = abs(x_high - x_low)
        if dx <= eps:
            diffs_x = np.diff(np.asarray(x_grid, dtype=float))
            pos_x = diffs_x[diffs_x > eps]
            dx = float(pos_x.min()) if pos_x.size > 0 else eps

        dy = abs(y_high - y_low)
        if dy <= eps:
            diffs_y = np.diff(np.asarray(y_grid, dtype=float))
            pos_y = diffs_y[diffs_y > eps]
            dy = float(pos_y.min()) if pos_y.size > 0 else eps

        inner_first_dimension = 0.0
        outer_first_dimension = 0.0
        first_dimension_length = dx
        open_angle = 0.0
        second_dimension_length = dy

        element_polygon = Polygon([
            (x_low, y_low),
            (x_low, y_high),
            (x_high, y_high),
            (x_high, y_low),
        ])

    else:
        raise ValueError(f"Unsupported Grid type: {Grid.type}")

    # --- Xác định vật liệu chiếm ưu thế bằng giao diện với các segment ---
    material_areas = defaultdict(float)
    segment_map = {}

    for seg in segments:
        try:
            inter = seg.polygon.intersection(element_polygon)
        except Exception as e:
            warnings.warn(f"Polygon intersection failed for segment {getattr(seg,'index', None)}: {e}")
            continue

        if not inter.is_empty:
            area = float(inter.area)
            material_areas[seg.material] += area
            if seg.material not in segment_map or segment_map[seg.material][0] < area:
                segment_map[seg.material] = (area, seg)

    total_area = float(element_polygon.area)
    covered_area = sum(material_areas.values())
    air_area = total_area - covered_area
    if air_area > 0:
        material_areas["air"] += air_area

    dominant_material = max(material_areas, key=material_areas.get) if material_areas else "air"
    dominant_segment = segment_map.get(dominant_material, (None, None))[1] if dominant_material in segment_map else None

    # --- Trường hợp toàn không khí ---
    if dominant_segment is None:
        fallback_axial = None
        for seg in segments:
            ax = getattr(seg, "axial_length", None)
            if ax not in (None, 0.0):
                fallback_axial = float(ax)
                break
        if fallback_axial is None and segments:
            fallback_axial = float(getattr(segments[0], "axial_length", 1.0) or 1.0)
        if fallback_axial is None:
            fallback_axial = 1.0

        return [
            "air",                  # 1 material
            0,                      # 2 index
            fallback_axial,         # 3 axial_length
            0.0,                    # 4 magnetic_source
            0.0,                    # 5 delta_angle_magnetic_source
            np.zeros((phase_number, 1)),       # 6 stator_excitation_coeffs
            0.0,                    # 7 delta_angle_stator_excitation
            float(first_dimension_length),   # 8 segment_first_dimension_length
            float(open_angle),                # 9 segment_opening_angle
            float(second_dimension_length),   # 10 segment_second_dimension_length
            float(inner_first_dimension),     # 11 inner_first_dimension
            float(outer_first_dimension),     # 12 outer_first_dimension
            float(first_dimension_length),    # 13 first_dimension_length
            float(open_angle),                # 14 open_angle
            float(second_dimension_length)    # 15 second_dimension_length
        ]

    # --- Nếu có segment chiếm ưu thế ---
    material = dominant_segment.material
    index = getattr(dominant_segment, "index", 0)
    axial_length = float(getattr(dominant_segment, "axial_length", 0.0) or 0.0)
    magnetic_source = float(getattr(dominant_segment, "magnetic_source", 0.0) or 0.0)
    delta_angle_magnetic_source = float(getattr(dominant_segment, "delta_angle_magnetic_source", 0.0) or 0.0)
    stator_excitation_coeffs = np.asarray(getattr(dominant_segment, "stator_excitation_coeffs", np.zeros((phase_number, 1))))
    delta_angle_stator_excitation = float(getattr(dominant_segment, "delta_angle_stator_excitation", 0.0) or 0.0)

    seg_first_dim_len = float(getattr(dominant_segment, "segment_first_dimension_length", None) or first_dimension_length)
    seg_opening_angle  = float(getattr(dominant_segment, "segment_opening_angle", None) or open_angle)
    seg_second_dim_len = float(getattr(dominant_segment, "segment_second_dimension_length", None) or second_dimension_length)

    return [
        material,                  # 1
        index,                     # 2
        axial_length,              # 3
        magnetic_source,           # 4
        delta_angle_magnetic_source, # 5
        stator_excitation_coeffs,  # 6
        delta_angle_stator_excitation, # 7
        seg_first_dim_len,         # 8
        seg_opening_angle,         # 9
        seg_second_dim_len,        # 10
        float(inner_first_dimension), # 11
        float(outer_first_dimension), # 12
        float(first_dimension_length), # 13
        float(open_angle),         # 14
        float(second_dimension_length), # 15
    ]
