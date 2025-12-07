def get_virtual_position(real_position, virtual_size):
    """
    real_position: chỉ số thực trong mảng 1 chiều
    virtual_size: tuple chứa kích thước ảo của mảng (n_rows, n_cols)
    Trả về tuple chứa vị trí ảo trong mảng 2 chiều (i, j)
    """
    n_rows, n_cols = virtual_size
    i = real_position // n_cols
    j = real_position % n_cols

    return (i, j)
