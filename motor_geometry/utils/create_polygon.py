from shapely.geometry import LineString, Polygon
from shapely.ops import unary_union, polygonize

def create_polygon(*lines):
    merged = unary_union(lines)
    polygons = list(polygonize(merged))
    if len(polygons) != 1:
        raise ValueError(f"create_polygon: mong đợi 1 polygon, nhưng nhận được {len(polygons)}")
    return polygons[0]

