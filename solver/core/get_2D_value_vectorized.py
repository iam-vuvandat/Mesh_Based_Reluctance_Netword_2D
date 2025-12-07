import numpy as np

def get_2D_value_vectorized(data,
                            index_2D,
                            virtual_size,
                            offset_vector=(0,0),
                            cyclic_type="no_cyclic"
                            ):
    """
    Truy cập vectorized vào mảng 1D giả lập mảng 2D, có offset và chế độ tuần hoàn.

    Parameters
    ----------
    data : np.ndarray
        Mảng 1 chiều chứa dữ liệu gốc, kích thước = virtual_size[0] * virtual_size[1].
    index_2D : np.ndarray
        Mảng 2xN, hàng 0 là chỉ số hàng (row), hàng 1 là chỉ số cột (col).
    virtual_size : tuple(int, int)
        Kích thước ảo (n_rows, n_cols).
    offset_vector : tuple(int, int)
        Độ lệch (dy, dx) áp dụng lên index_2D.
    cyclic_type : str
        Kiểu tuần hoàn, gồm:
        - "no_cyclic": không tuần hoàn, vượt mảng trả về 0.0
        - "first_dimension": tuần hoàn theo cột
        - "second_dimension": tuần hoàn theo hàng
        - "full_cyclic": tuần hoàn theo cả hai chiều

    Returns
    -------
    value : np.ndarray
        Mảng giá trị tương ứng, nếu vượt mảng thì trả về 0.0.
    valid : np.ndarray
        Mảng 0/1, giá trị 1 nếu truy cập hợp lệ, 0 nếu không hợp lệ.

    Example
    -------
    >>> data = np.arange(9)
    >>> idx2D = np.array([[0, 1, 2], [0, 1, 2]])
    >>> get_2D_value_vectorized(data, idx2D, (3, 3), offset_vector=(1, -1))
    (array([3., 4., 0.]), array([1, 1, 0]))
    """

    n_rows, n_cols = virtual_size
    dy, dx = offset_vector

    # --- Tách chỉ số hàng / cột ---
    row = index_2D[0] + dy
    col = index_2D[1] + dx

    # --- Xử lý cyclic ---
    if cyclic_type == "no_cyclic":
        valid = (
            (row >= 0) & (row < n_rows) &
            (col >= 0) & (col < n_cols)
        ).astype(int)
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

    # --- Chuyển chỉ số 2D → 1D ---
    index_1D = row * n_cols + col

    # --- Lấy giá trị ---
    value = np.zeros_like(row, dtype=float)
    valid_mask = valid.astype(bool)

    if np.any(valid_mask):
        value[valid_mask] = data[index_1D[valid_mask]]

    # --- Loại bỏ giá trị không hợp lệ ---
    value = value * valid

    return value, valid
