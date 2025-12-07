def find_polar_grid_size(polar_coords):
    """Trả về (số ô hướng xuyên tâm, số ô hướng tiếp tuyến)."""
    r_grid = polar_coords[0]
    theta_grid = polar_coords[1]
    size = (len(r_grid) - 1, len(theta_grid) - 1)  
    return size
