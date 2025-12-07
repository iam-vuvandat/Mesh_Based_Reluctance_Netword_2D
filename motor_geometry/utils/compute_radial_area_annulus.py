import math

def compute_radial_area_annulus(inner_radius, outer_radius, open_angle, axial_length):
    """
    Compute the logarithmic mean cross-sectional area of an annulus sector 
    (radial direction).

    Formula:
        A = (Δr / ln(r_out / r_in)) * L * Δθ
    where:
        Δr   = r_out - r_in
        r_in = inner radius
        r_out = outer radius
        L    = axial length
        Δθ   = opening angle (rad)

    If r_out ≈ r_in, the limit is:
        A = r * L * Δθ

    Parameters:
        inner_radius (float): Inner radius (m)
        outer_radius (float): Outer radius (m)
        open_angle (float): Angular span of the annulus sector (rad)
        axial_length (float): Axial length (m)

    Returns:
        float: Logarithmic mean cross-sectional area (m^2)
    """
    if inner_radius <= 0 or outer_radius <= 0:
        raise ValueError("Radii must be positive.")
    if abs(outer_radius - inner_radius) < 1e-12:
        # Limit as r_out → r_in
        return open_angle * axial_length * inner_radius

    return open_angle * axial_length * (outer_radius - inner_radius) / math.log(outer_radius / inner_radius)
