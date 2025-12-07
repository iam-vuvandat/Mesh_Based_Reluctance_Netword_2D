import numpy as np
from motor_geometry.models.Grid import Grid

def create_trapezoid_grid(first_dimension_begin, first_dimension_end, npoint_first_dimension,
                          second_dimension_begin, second_dimension_end, npoint_second_dimension):
    """
    Tạo lưới Trapezoid và trả về đối tượng Grid.
    Grid.grid_coordinate có dạng [theta_array, r_array] giống polar_coords.

    Parameters
    ----------
    first_dimension_begin, first_dimension_end : float
        Giới hạn chiều thứ nhất (theta)
    second_dimension_begin, second_dimension_end : float
        Giới hạn chiều thứ hai (r)
    npoint : int
        Số điểm theo mỗi chiều

    Returns
    -------
    grid : Grid
        Đối tượng Grid với grid_coordinate = [theta_array, r_array]
    """
    theta_array = np.linspace(first_dimension_begin, first_dimension_end, npoint_first_dimension)
    r_array = np.linspace(second_dimension_begin, second_dimension_end, npoint_second_dimension)

    # Trả về list gồm 2 numpy array, giống polar_coords
    grid_coords = [theta_array, r_array]

    return Grid(grid_coords, grid_type="trapezoid")
