def compute_average_tangential_length(inner_radius, outer_radius, open_angle):
    """
    Tính chiều dài trung bình khi đi theo hướng tangential trong một vành khăn.
    
    Parameters:
        inner_radius (float): bán kính trong (R_trong)
        outer_radius (float): bán kính ngoài (R_ngoài)
        open_angle (float): góc quét theo radian

    Returns:
        float: chiều dài tangential trung bình hợp lý nhất
    """
    # Bán kính trung bình thực sự theo diện tích
    r_true = (2/3) * (outer_radius**3 - inner_radius**3) / (outer_radius**2 - inner_radius**2)
    
    # Chiều dài tangential
    average_tangential_length = r_true * open_angle
    
    return average_tangential_length
