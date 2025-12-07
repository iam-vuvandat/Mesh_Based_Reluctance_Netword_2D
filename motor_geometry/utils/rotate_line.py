import math
from shapely.geometry import LineString

def rotate_line(line, alpha):
    """Xoay một LineString quanh gốc (0,0) góc alpha (radian)."""
    def rotate_point(x, y, a):
        xr = x*math.cos(a) - y*math.sin(a)
        yr = x*math.sin(a) + y*math.cos(a)
        return xr, yr

    coords = list(line.coords)
    new_coords = [rotate_point(x, y, alpha) for x, y in coords]
    return LineString(new_coords)
