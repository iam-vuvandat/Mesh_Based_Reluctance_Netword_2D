import math

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

def rotate_point(point, theta):
    """
    Xoay điểm point quanh gốc (0, 0) một góc theta (radian) ngược chiều kim đồng hồ.
    Trả về một Point mới với tọa độ đã xoay.
    """
    x_new = point.x * math.cos(theta) - point.y * math.sin(theta)
    y_new = point.x * math.sin(theta) + point.y * math.cos(theta)
    return Point(x_new, y_new)