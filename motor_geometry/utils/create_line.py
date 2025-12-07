from shapely.geometry import LineString

def create_line(x_coords, y_coords):
    """
    Tạo một LineString từ hai mảng hoành độ và tung độ.

    Args:
        x_coords (list or array): Mảng hoành độ.
        y_coords (list or array): Mảng tung độ.

    Returns:
        LineString: Đối tượng LineString từ shapely.
    """
    if len(x_coords) != len(y_coords):
        raise ValueError("Độ dài của x_coords và y_coords phải bằng nhau.")
    points = list(zip(x_coords, y_coords))
    return LineString(points)