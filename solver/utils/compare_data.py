import numpy as np
from sklearn.metrics import mean_squared_error
from scipy.interpolate import interp1d

def compare_data(data_true, data_pred, num_points=15):
    """
    So sánh 2 sóng (có thể khác mật độ) bằng NRMSE (%).
    
    Hàm này nội suy bậc 2 (quadratic) cả hai sóng về `num_points` (100)
    điểm chung trên khoảng X giao nhau trước khi so sánh.
    
    Cấu trúc input: [0] là Y (dữ liệu), [-1] là X (vị trí).
    """
    
    try:
        # 1. Trích xuất và sắp xếp dữ liệu X, Y
        # (Nội suy yêu cầu X phải được sắp xếp)
        y_true_raw, x_true_raw = data_true[0], data_true[-1]
        sort_idx_true = np.argsort(x_true_raw)
        x_true, y_true = x_true_raw[sort_idx_true], y_true_raw[sort_idx_true]

        y_pred_raw, x_pred_raw = data_pred[0], data_pred[-1]
        sort_idx_pred = np.argsort(x_pred_raw)
        x_pred, y_pred = x_pred_raw[sort_idx_pred], y_pred_raw[sort_idx_pred]
    
    except IndexError:
        print("Lỗi: Cấu trúc data input sai (không tìm thấy [0] hoặc [-1]).")
        return np.inf

    # 2. Tìm khoảng X giao nhau
    start_common = max(np.min(x_true), np.min(x_pred))
    end_common = min(np.max(x_true), np.max(x_pred))

    if start_common >= end_common:
        print("Cảnh báo: Hai dải X không giao nhau.")
        return np.inf

    # 3. Tạo trục X chuẩn hóa (num_points điểm)
    x_common = np.linspace(start_common, end_common, num_points)

    # 4. Nội suy bậc 2 (quadratic)
    # (Dự phòng 'linear' nếu không đủ điểm cho bậc 2)
    kind_true = 'quadratic' if len(x_true) > 2 else 'linear'
    kind_pred = 'quadratic' if len(x_pred) > 2 else 'linear'

    interp_true = interp1d(x_true, y_true, kind=kind_true, bounds_error=False, fill_value=np.nan)
    interp_pred = interp1d(x_pred, y_pred, kind=kind_pred, bounds_error=False, fill_value=np.nan)

    y_true_resampled = interp_true(x_common)
    y_pred_resampled = interp_pred(x_common)

    # Lọc NaNs (nếu nội suy bị thất bại ở biên)
    valid_mask = ~np.isnan(y_true_resampled) & ~np.isnan(y_pred_resampled)
    y_true_common = y_true_resampled[valid_mask]
    y_pred_common = y_pred_resampled[valid_mask]

    if len(y_true_common) < 2:
        print("Cảnh báo: Không đủ điểm chung sau khi nội suy.")
        return np.inf

    # 5. Tính NRMSE
    rmse = np.sqrt(mean_squared_error(y_true_common, y_pred_common))
    y_range = np.max(y_true_common) - np.min(y_true_common)

    # Xử lý chia cho 0 (nếu sóng chuẩn là đường thẳng)
    if y_range == 0:
        return 0.0 if rmse == 0 else np.inf
    
    nrmse = rmse / y_range
    return nrmse * 100

