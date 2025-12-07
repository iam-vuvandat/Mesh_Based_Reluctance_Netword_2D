def find_grid_size(grid):
    """
    Nhận vào một grid, trả về tuple chứa số ô hàng, số ô cột
    Số ô hàng: kích cỡ trục y ( hoặc radial ) (second_dimension) - 1
    số ô cột: kích cỡ trục x ( hoặc tangential) (first_dimension) - 1
    """
    first_dimenstion = grid.grid_coordinate[1]
    second_dimenstion = grid.grid_coordinate[0]

    size = (len(second_dimenstion) - 1 , len(first_dimenstion) - 1)
    return size
    