from shapely.geometry import Polygon

def create_rectangle(first_point, second_point):
    """
    Tạo polygon hình chữ nhật từ first_point và second_point.
    Các point là tuple (x1, y1) và (x2, y2).
    
    Trả về một shapely Polygon.
    """
    x1, y1 = first_point
    x2, y2 = second_point

    # Tìm min/max để tránh thứ tự điểm ngược
    xmin, xmax = min(x1, x2), max(x1, x2)
    ymin, ymax = min(y1, y2), max(y1, y2)

    # Các đỉnh của hình chữ nhật theo thứ tự (ngược chiều kim đồng hồ)
    coords = [(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)]

    return Polygon(coords)
