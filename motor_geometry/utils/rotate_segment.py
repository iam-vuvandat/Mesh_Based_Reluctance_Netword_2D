from shapely.affinity import rotate
from motor_geometry.models.Segment import Segment

def rotate_segment(segment, angle_rad, origin=(0, 0)):
    """
    Xoay polygon của một segment quanh origin, giữ nguyên các thuộc tính khác.

    Parameters
    ----------
    segment : Segment
        Đối tượng Segment.
    angle_rad : float
        Góc xoay (radian).
    origin : tuple
        Tọa độ tâm xoay (mặc định là (0,0)).

    Returns
    -------
    Segment
        Segment mới với polygon đã xoay, các thuộc tính khác giữ nguyên.
    """
    # Xoay polygon
    poly_rot = rotate(segment.polygon, angle_rad, origin=origin, use_radians=True)

    # Trả về Segment mới với đủ tham số
    return Segment(
        poly_rot,
        segment.material,
        segment.index,
        segment.axial_length,
        segment.magnetic_source,
        segment.delta_angle_magnetic_source,
        segment.stator_excitation_coeffs,
        segment.delta_angle_stator_excitation
    )
