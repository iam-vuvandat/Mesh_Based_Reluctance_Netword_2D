import numpy as np

def get_1D_index_vectorized(index_2D,
                            virtual_size,
                            offset_vector=(0, 0),
                            cyclic_type="no_cyclic"):
    """
    Chuyển chỉ số 2D → 1D với offset và cyclic boundary handling.

    Parameters
    ----------
    index_2D : np.ndarray
        Mảng 2xN, hàng 0 = row, hàng 1 = col.
    virtual_size : tuple(int, int)
        Kích thước ảo (n_rows, n_cols).
    offset_vector : tuple(int, int)
        (dy, dx) offset áp dụng.
    cyclic_type : str
        Kiểu tuần hoàn:
        - "no_cyclic": vượt mảng trả về value=0, valid=0
        - "first_dimension": tuần hoàn theo cột
        - "second_dimension": tuần hoàn theo hàng
        - "full_cyclic": tuần hoàn cả hai chiều

    Returns
    -------
    value : np.ndarray
        Chỉ số 1D tương ứng, 0 nếu invalid.
    valid : np.ndarray
        Mảng 0/1, 1 nếu hợp lệ.
    """

    n_rows, n_cols = virtual_size
    dy, dx = offset_vector

    # --- Áp offset ---
    row = index_2D[0] + dy
    col = index_2D[1] + dx

    # --- Xử lý cyclic ---
    if cyclic_type == "no_cyclic":
        valid = ((row >= 0) & (row < n_rows) &
                 (col >= 0) & (col < n_cols)).astype(int)
    elif cyclic_type == "first_dimension":  # tuần hoàn cột
        valid = ((row >= 0) & (row < n_rows)).astype(int)
        col = np.mod(col, n_cols)
    elif cyclic_type == "second_dimension":  # tuần hoàn hàng
        valid = ((col >= 0) & (col < n_cols)).astype(int)
        row = np.mod(row, n_rows)
    elif cyclic_type == "full_cyclic":
        valid = np.ones_like(row, dtype=int)
        row = np.mod(row, n_rows)
        col = np.mod(col, n_cols)
    else:
        raise ValueError("cyclic_type must be one of: 'no_cyclic', 'first_dimension', 'second_dimension', 'full_cyclic'")

    # --- Chuyển 2D → 1D ---
    index_1D = row * n_cols + col

    # --- Loại bỏ giá trị không hợp lệ ---
    value = index_1D * valid

    return value, valid
