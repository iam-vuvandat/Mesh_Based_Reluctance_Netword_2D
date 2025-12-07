from shapely.geometry import Point, LineString
from motor_geometry.utils.create_line import create_line

def create_line_from_points(point1: Point, point2: Point) -> LineString:
    """
    Tạo một LineString từ hai đối tượng Point.

    Args:
        point1 (Point): Điểm đầu.
        point2 (Point): Điểm cuối.

    Returns:
        LineString: Đối tượng LineString nối hai điểm.
    """ 
    x= [point1.x, point2.x]
    y = [point1.y, point2.y]
    line=create_line(x,y)
    return line