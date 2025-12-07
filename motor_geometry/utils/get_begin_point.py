from shapely.geometry import LineString, Point

def get_begin_point(line: LineString) -> Point:
    """
    Nhận vào một đường thẳng (LineString), trả về điểm đầu (Point) của đường đó.
    """
    return Point(line.coords[0])

