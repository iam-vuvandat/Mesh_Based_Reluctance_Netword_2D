from shapely.geometry import LineString, Point

def get_end_point(line: LineString) -> Point:
    """
    Nhận vào một LineString và trả về điểm cuối (Point) của đường đó.
    """
    return Point(line.coords[-1])