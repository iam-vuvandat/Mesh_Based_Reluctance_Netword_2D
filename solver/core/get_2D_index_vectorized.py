import numpy as np

def get_2D_index_vectorized(index_1D_input=0,
                            virtual_size=(0, 0),
                            offset_vector=(0, 0),
                            cyclic_type="no_cyclic"):
    """
    Vectorized conversion from 1D flattened indices to 2D indices
    with offset and cyclic boundary handling.

    Parameters
    ----------
    index_1D_input : array-like or int
        1D indices of a flattened array.
    virtual_size : tuple(int, int)
        Virtual 2D size (n_rows, n_cols).
    offset_vector : tuple(int, int)
        (dy, dx) offset applied to 2D indices.
    cyclic_type : str
        Boundary handling mode:
        - "no_cyclic"         : indices outside range are invalid (-1)
        - "first_dimension"   : cyclic along columns only
        - "second_dimension"  : cyclic along rows only
        - "full_cyclic"       : cyclic along both rows and columns

    Returns
    -------
    tuple(np.ndarray, np.ndarray)
        index_2D : (2, N)
            - First row: row indices
            - Second row: column indices
            Invalid positions are set to (-1, -1).
        valid : (N,)
            - 1 if valid, 0 if invalid.
    """

    # --- Kiểm tra tham số ---
    if not isinstance(virtual_size, tuple) or len(virtual_size) != 2:
        raise TypeError("virtual_size must be a tuple (n_rows, n_cols)")
    n_rows, n_cols = virtual_size

    if isinstance(index_1D_input, (int, np.integer)):
        index_1D_input = np.array([index_1D_input], dtype=int)
    else:
        index_1D_input = np.array(index_1D_input, dtype=int)

    # --- Tính chỉ số hàng và cột cơ sở ---
    row_index = index_1D_input // n_cols
    col_index = index_1D_input % n_cols

    # --- Áp dụng offset ---
    dy, dx = offset_vector
    row_index = row_index + dy
    col_index = col_index + dx

    # --- Xử lý theo cyclic_type ---
    if cyclic_type == "no_cyclic":
        valid = ((row_index >= 0) & (row_index < n_rows) &
                 (col_index >= 0) & (col_index < n_cols)).astype(np.int8)
        row_index = np.where(valid, row_index, -1)
        col_index = np.where(valid, col_index, -1)

    elif cyclic_type == "first_dimension":  # tuần hoàn theo cột
        valid = ((row_index >= 0) & (row_index < n_rows)).astype(np.int8)
        col_index = np.mod(col_index, n_cols)
        row_index = np.where(valid, row_index, -1)
        col_index = np.where(valid, col_index, -1)

    elif cyclic_type == "second_dimension":  # tuần hoàn theo hàng
        valid = ((col_index >= 0) & (col_index < n_cols)).astype(np.int8)
        row_index = np.mod(row_index, n_rows)
        row_index = np.where(valid, row_index, -1)
        col_index = np.where(valid, col_index, -1)

    elif cyclic_type == "full_cyclic":  # tuần hoàn cả hai chiều
        valid = np.ones_like(row_index, dtype=np.int8)
        row_index = np.mod(row_index, n_rows)
        col_index = np.mod(col_index, n_cols)

    else:
        raise ValueError(
            "cyclic_type must be one of: 'no_cyclic', 'first_dimension', 'second_dimension', 'full_cyclic'"
        )

    # --- Trả kết quả ---
    index_2D = np.vstack((row_index, col_index))
    return index_2D, valid
