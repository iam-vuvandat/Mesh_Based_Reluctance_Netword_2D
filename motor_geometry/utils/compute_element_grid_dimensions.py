def compute_element_grid_dimensions(position, Grid):
    """
    Tính toán kích thước element dựa trên vị trí và lưới.
    Tương thích với cả lưới "polar" và lưới "cartesian".

    Trả về tuple:
    (inner_first_dimension,
     outer_first_dimension,
     first_dimension_length,
     open_angle,               # !=0 với polar, =0 với cartesian
     second_dimension_length)
    """
    line, col = position

    if Grid.type == "polar":
        theta, r = Grid.grid_coordinate  # first_dimension = theta (tangential), second_dimension = r (radial)
        r_inner = float(r[line])
        r_outer = float(r[line + 1])
        arc_angle = abs(theta[col + 1] - theta[col])

        first_dimension_length = (r_inner + r_outer) / 2.0 * arc_angle  # tangential arc length
        open_angle = arc_angle
        second_dimension_length = abs(r_outer - r_inner)  # radial length

        return (
            r_inner,
            r_outer,
            first_dimension_length,
            open_angle,
            second_dimension_length
        )

    elif Grid.type == "cartesian":
        x, y = Grid.grid_coordinate  # first_dimension = X, second_dimension = Y
        x_start = float(x[col])
        x_end   = float(x[col + 1])
        y_start = float(y[line])
        y_end   = float(y[line + 1])

        first_dimension_length = abs(x_end - x_start)   # tangential / X
        open_angle = 0.0
        second_dimension_length = abs(y_end - y_start)  # radial / Y

        return (
            0.0,
            0.0,
            first_dimension_length,
            open_angle,
            second_dimension_length
        )

    else:
        raise ValueError(f"Unsupported Grid type: {Grid.type}")
