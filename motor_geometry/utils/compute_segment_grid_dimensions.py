from shapely.geometry import Polygon
import numpy as np

def compute_segment_grid_dimensions(segment, grid):
    """
    Tính toán kích thước segment trong Grid (polar, cartesian, trapezoid).
    Luôn trả về giá trị chiều dài dương, kể cả khi grid có tọa độ âm.
    """
    seg_poly = segment.polygon
    gtype = grid.type
    coords = grid.grid_coordinate  # [first_dimension, second_dimension]
    n_rows, n_cols = grid.size

    cell_first_indices = []
    cell_second_indices = []

    if gtype == "polar":
        if len(coords) != 2:
            raise ValueError("Polar grid_coordinate phải là list [theta_array, r_array]")
        theta_array, r_array = coords

        for i in range(len(r_array)-1):
            for j in range(len(theta_array)-1):
                cell_poly = create_sector_polygon(theta_array[j], theta_array[j+1],
                                                  r_array[i], r_array[i+1])
                inter = seg_poly.intersection(cell_poly)
                if not inter.is_empty and inter.area / cell_poly.area > 0.5:
                    cell_first_indices.append(j)
                    cell_second_indices.append(i)

        if cell_first_indices:
            theta_min = theta_array[min(cell_first_indices)]
            theta_max = theta_array[max(cell_first_indices)+1]
            r_min = r_array[min(cell_second_indices)]
            r_max = r_array[max(cell_second_indices)+1]
            r_avg = 0.5 * (r_min + r_max)
            segment.segment_first_dimension_length = abs(theta_max - theta_min) * r_avg
            segment.segment_opening_angle = abs(theta_max - theta_min)
        else:
            segment.segment_first_dimension_length = 0.0
            segment.segment_opening_angle = 0.0

        if cell_second_indices:
            r_min = r_array[min(cell_second_indices)]
            r_max = r_array[max(cell_second_indices)+1]
            segment.segment_second_dimension_length = abs(r_max - r_min)
        else:
            segment.segment_second_dimension_length = 0.0

    elif gtype == "cartesian":
        if len(coords) != 2:
            raise ValueError("Cartesian grid_coordinate phải là list [x_array, y_array]")
        x_array, y_array = coords

        for i in range(len(y_array)-1):
            for j in range(len(x_array)-1):
                cell_poly = create_rectangle_polygon(x_array[j], x_array[j+1],
                                                     y_array[i], y_array[i+1])
                inter = seg_poly.intersection(cell_poly)
                if not inter.is_empty and inter.area / cell_poly.area > 0.5:
                    cell_first_indices.append(j)
                    cell_second_indices.append(i)

        if cell_first_indices:
            x_min = x_array[min(cell_first_indices)]
            x_max = x_array[max(cell_first_indices)+1]
            segment.segment_first_dimension_length = abs(x_max - x_min)
        else:
            segment.segment_first_dimension_length = 0.0

        if cell_second_indices:
            y_min = y_array[min(cell_second_indices)]
            y_max = y_array[max(cell_second_indices)+1]
            segment.segment_second_dimension_length = abs(y_max - y_min)
        else:
            segment.segment_second_dimension_length = 0.0

        segment.segment_opening_angle = 0.0

    elif gtype == "trapezoid":
        if len(coords) != 2:
            raise ValueError("Trapezoid grid_coordinate phải là list [theta_array, r_array]")
        theta_array, r_array = coords

        for i in range(len(r_array)-1):
            for j in range(len(theta_array)-1):
                cell_poly = create_trapezoid_polygon(theta_array[j], theta_array[j+1],
                                                     r_array[i], r_array[i+1])
                inter = seg_poly.intersection(cell_poly)
                if not inter.is_empty and inter.area / cell_poly.area > 0.5:
                    cell_first_indices.append(j)
                    cell_second_indices.append(i)

        if cell_first_indices:
            theta_min = theta_array[min(cell_first_indices)]
            theta_max = theta_array[max(cell_first_indices)+1]
            r_min = r_array[min(cell_second_indices)]
            r_max = r_array[max(cell_second_indices)+1]

            arc_outer = r_max * abs(theta_max - theta_min)
            arc_inner = r_min * abs(theta_max - theta_min)
            segment.segment_first_dimension_length = 0.5 * (arc_outer + arc_inner)
            segment.segment_opening_angle = abs(theta_max - theta_min)
        else:
            segment.segment_first_dimension_length = 0.0
            segment.segment_opening_angle = 0.0

        if cell_second_indices:
            r_min = r_array[min(cell_second_indices)]
            r_max = r_array[max(cell_second_indices)+1]
            segment.segment_second_dimension_length = abs(r_max - r_min)
        else:
            segment.segment_second_dimension_length = 0.0

    else:
        raise ValueError(f"Unsupported grid type: {gtype}")


def create_sector_polygon(theta1, theta2, r_in, r_out, n_points=10):
    """Polygon hình quạt cho grid polar"""
    outer_arc = [(r_out * np.cos(t), r_out * np.sin(t)) 
                 for t in np.linspace(theta1, theta2, n_points)]
    inner_arc = [(r_in * np.cos(t), r_in * np.sin(t)) 
                 for t in np.linspace(theta2, theta1, n_points)]
    return Polygon(outer_arc + inner_arc)

def create_rectangle_polygon(x1, x2, y1, y2):
    """Polygon hình chữ nhật cho grid cartesian"""
    return Polygon([(x1, y1), (x2, y1), (x2, y2), (x1, y2)])

def create_trapezoid_polygon(theta1, theta2, r_in, r_out):
    """Polygon hình thang cân cho grid trapezoid (4 đỉnh)"""
    return Polygon([
        (r_in * np.cos(theta1), r_in * np.sin(theta1)),
        (r_in * np.cos(theta2), r_in * np.sin(theta2)),
        (r_out * np.cos(theta2), r_out * np.sin(theta2)),
        (r_out * np.cos(theta1), r_out * np.sin(theta1)),
    ])
