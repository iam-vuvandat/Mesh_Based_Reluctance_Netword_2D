def get_linear_index(position: tuple[int, int], virtual_size: tuple[int, int],cyclic_type ) -> int | None:
    """
    Chuyển đổi chỉ số (i, j) trong ma trận 2D ảo sang chỉ số 1D.
    - Có tính chất tuần hoàn tùy chỉnh
    """
    if not isinstance(position, tuple) or len(position) != 2:
        raise TypeError("position phải là tuple (i, j)")

    if not isinstance(virtual_size, tuple) or len(virtual_size) != 2:
        raise TypeError("virtual_size phải là tuple (n_rows, n_cols)")

    i, j = position
    n_rows, n_cols = virtual_size

    if not isinstance(i, int) or not isinstance(j, int):
        raise TypeError("i và j phải là số nguyên (int)")

    if cyclic_type == "no_cyclic":
        if i>= n_rows or i<0:
            return None
        elif j>= n_cols or j<0:
            return None
        else:
            return (i * n_cols) + j

    elif cyclic_type =="first_dimension":
        if i >= n_rows or i < 0:
            return None
        else:
            j = j % n_cols
            return (i * n_cols) + j
        
    elif cyclic_type =="second_dimension":
        if j >= n_cols or j<0:
            return None
        else:
            i = i % n_rows
            return (i * n_cols) + j
        
    else:
        i = i % n_rows
        j = j % n_cols
        return (i * n_cols) + j

    
