import numpy as np

def exclude_invalid_columns_vectorized(a1, a2, a3, valid):
    """
    Loại bỏ các giá trị không hợp lệ từ 3 mảng 1D numpy,
    dựa vào mảng thứ 4 (valid). Trả về 3 mảng 1D đã lọc.

    Parameters
    ----------
    a1, a2, a3 : np.ndarray
        Các mảng numpy 1D cần lọc.
    valid : np.ndarray
        Mảng 1D 0/1, đánh dấu giá trị hợp lệ.

    Returns
    -------
    tuple of np.ndarray
        (a1_filtered, a2_filtered, a3_filtered)
        Các mảng 1D đã loại bỏ các giá trị invalid.
    """

    valid_mask = np.array(valid, dtype=bool)

    # Lọc từng mảng
    a1_filtered = np.array(a1, copy=True).flatten()[valid_mask]
    a2_filtered = np.array(a2, copy=True).flatten()[valid_mask]
    a3_filtered = np.array(a3, copy=True).flatten()[valid_mask]

    return a1_filtered, a2_filtered, a3_filtered
