from motor_geometry.models.Grid import Grid
import numpy as np

def create_polar_grid(theta_begin, theta_end, n_theta,  r_in, r_out, n_r):
    """
    Tạo một lưới cực dựa trên góc bắt đầu, góc kết thúc, bán kính trong và ngoài và số điểm tương ứng
    """
    theta_array = np.linspace(theta_begin,theta_end,n_theta)
    r_array = np.linspace(r_in, r_out,n_r)

    grid_coords = [theta_array, r_array]

    return Grid(grid_coords, grid_type="polar")