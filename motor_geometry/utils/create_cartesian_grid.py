import numpy as np
from motor_geometry.models.Grid import Grid

def create_cartesian_grid(first_dimension_begin, first_dimension_end, npoint_first_dimension,
                          second_dimension_begin, second_dimension_end, npoint_second_dimension):
    """
    Tạo lưới Cartesian và trả về đối tượng Grid.
    Grid.grid_coordinate có dạng [x_array, y_array] giống polar_coords.

    Parameters
    ----------
    first_dimension_begin, first_dimension_end : float
        Giới hạn chiều thứ nhất (X)
    second_dimension_begin, second_dimension_end : float
        Giới hạn chiều thứ hai (Y)
    npoint : int
        Số điểm theo mỗi chiều

    Returns
    -------
    grid : Grid
        Đối tượng Grid với grid_coordinate = [x_array, y_array]
    """
    X = np.linspace(first_dimension_begin, first_dimension_end, npoint_first_dimension)
    Y = np.linspace(second_dimension_begin, second_dimension_end, npoint_second_dimension)

    # Trả về list gồm 2 numpy array, giống polar_coords
    grid_coords = [X, Y]

    return Grid(grid_coords, grid_type="cartesian")
