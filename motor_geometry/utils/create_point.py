from shapely.geometry import Point

def create_point(x, y):
    """
    Tạo một đối tượng Point từ tọa độ x và y.

    Parameters
    ----------
    x : float
        Tọa độ x
    y : float
        Tọa độ y

    Returns
    -------
    Point
        Đối tượng Point tại (x, y)
    """
    return Point(x, y)
