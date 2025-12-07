import numpy as np
from motor_geometry.utils.create_line import create_line

def create_arc(radius, theta1, theta2, num_points=100):
    """
    Tạo một cung tròn LineString.
    radius: bán kính cung tròn
    theta1: góc bắt đầu (radian)
    theta2: góc kết thúc (radian)
    num_points: số điểm trên cung
    """
    thetas = np.linspace(theta1, theta2, num_points)
    x_coords = radius * np.cos(thetas)
    y_coords = radius * np.sin(thetas)
    return create_line(x_coords, y_coords)
