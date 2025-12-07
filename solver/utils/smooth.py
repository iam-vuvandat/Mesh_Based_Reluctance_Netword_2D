import numpy as np
from scipy.interpolate import interp1d

def smooth(array, points=2000, method='quadratic'):
    """
    Làm mượt dữ liệu dạng [y1, y2, ..., theta]
    bằng nội suy bậc 2 (hoặc kiểu khác).
    
    Parameters
    ----------
    array : np.ndarray
        Ma trận dữ liệu, trong đó:
        - Các hàng 0 → n-2 là giá trị (y)
        - Hàng cuối cùng (-1) là biến x (thường là góc rôto)
    points : int, optional
        Số điểm sau khi nội suy (mặc định 2000)
    method : str, optional
        Kiểu nội suy: 'linear', 'quadratic', hoặc 'cubic' (mặc định: 'quadratic')
    
    Returns
    -------
    np.ndarray
        Ma trận dữ liệu mới có cùng số hàng, nhưng nhiều điểm hơn.
    """

    # --- Tách biến ---
    x = array[-1, :]
    y_rows = array[:-1, :]

    # --- Tạo lưới theta mịn hơn ---
    x_smooth = np.linspace(x.min(), x.max(), points)
    y_smooth_rows = []

    # --- Nội suy từng hàng ---
    for y in y_rows:
        f_interp = interp1d(x, y, kind=method)
        y_smooth = f_interp(x_smooth)
        y_smooth_rows.append(y_smooth)

    # --- Ghép lại định dạng gốc ---
    smoothed_array = np.vstack(y_smooth_rows + [x_smooth])
    return smoothed_array
