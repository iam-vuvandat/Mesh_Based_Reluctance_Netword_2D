import numpy as np

MU0 = 4 * np.pi * 1e-7  # H/m

def lookup_BH_curve(
    B_input,
    material_database,
    return_du_dB=False,
    material_filter=None,
    invert=False
):
    """
    Vectorized B-H lookup for multiple materials (air, magnet, iron),
    supporting both 1D and 2D B_input arrays.

    Parameters
    ----------
    B_input : np.ndarray
        Magnetic flux density (B) [T]. Shape (m, n)
    material_database : object
        Must contain:
          - air.relative_permeance
          - magnet.relative_permeance
          - iron.B_H_curve["B_data"], iron.B_H_curve["H_data"]
    return_du_dB : bool
        If True, returns derivative d(mu_r)/dB as well.
    material_filter : (1, n) or (n,) np.ndarray[int]
        Material per column:
            0 = air
            1 = magnet
            2 = iron
    invert : bool
        If True, returns 1/mu_r

    Returns
    -------
    [mu_r, dmu_r_dB] : list of np.ndarray
        Same shape as B_input
    """

    # --- Step 1. Chuẩn hóa đầu vào ---
    is_scalar = np.isscalar(B_input)
    B_array = np.atleast_1d(np.asarray(B_input, dtype=float))
    shape_B = B_array.shape

    if B_array.ndim == 1:
        B_array = B_array.reshape(-1, 1)  # (m, 1)

    m, n = B_array.shape

    # --- Step 2. Xử lý material_filter (theo cột) ---
    if material_filter is None:
        material_filter = np.full((1, n), 2, dtype=int)  # default: all iron
    else:
        material_filter = np.asarray(material_filter, dtype=int).reshape(1, -1)
        if material_filter.shape[1] != n:
            raise ValueError("material_filter must have shape (1, n) matching number of columns in B_input")

    # Tạo mask (m, n) cho toàn bộ B_input
    material_filter_2d = np.repeat(material_filter, m, axis=0)

    # --- Step 3. Lấy bảng B-H ---
    B_TABLE = np.asarray(material_database.iron.B_H_curve["B_data"], dtype=float)
    H_TABLE = np.asarray(material_database.iron.B_H_curve["H_data"], dtype=float)
    B_min, B_max = B_TABLE[0], B_TABLE[-1]

    # --- Step 4. Nội suy ---
    B_clip = np.clip(np.abs(B_array), B_min, B_max)
    H_val = np.interp(B_clip, B_TABLE, H_TABLE)

    delta_B = 1e-3
    H_delta = np.interp(delta_B, B_TABLE, H_TABLE)
    mu_at_zero = delta_B / (H_delta + 1e-15)
    mu_iron = np.where(np.abs(H_val) < 1e-9,
                       mu_at_zero,
                       B_clip / (H_val + 1e-15)) / MU0

    # --- Step 5. d(mu)/dB ---
    if return_du_dB:
        h = 1e-4
        B_plus = np.clip(B_clip + h, B_min, B_max)
        B_minus = np.clip(B_clip - h, B_min, B_max)
        H_plus = np.interp(B_plus, B_TABLE, H_TABLE)
        H_minus = np.interp(B_minus, B_TABLE, H_TABLE)
        mu_plus = np.where(np.abs(H_plus) < 1e-9, mu_at_zero, B_plus / (H_plus + 1e-15)) / MU0
        mu_minus = np.where(np.abs(H_minus) < 1e-9, mu_at_zero, B_minus / (H_minus + 1e-15)) / MU0
        denom = (B_plus - B_minus)
        dmu_iron = np.where(np.abs(denom) < 1e-15, 0.0, (mu_plus - mu_minus) / denom)
    else:
        dmu_iron = np.zeros_like(mu_iron)

    # --- Step 6. Áp vật liệu ---
    mu_result = np.empty_like(B_array)
    dmu_result = np.empty_like(B_array)

    mask_air = (material_filter_2d == 0)
    mask_magnet = (material_filter_2d == 1)
    mask_iron = (material_filter_2d == 2)

    mu_result[mask_air] = material_database.air.relative_permeance
    mu_result[mask_magnet] = material_database.magnet.relative_permeance
    mu_result[mask_iron] = mu_iron[mask_iron]

    dmu_result[mask_air | mask_magnet] = 0.0
    dmu_result[mask_iron] = dmu_iron[mask_iron]

    # --- Step 7. Nghịch đảo (nếu cần) ---
    if invert:
        mu_result = 1.0 / (mu_result + 1e-30)

    # --- Step 8. Kết quả ---
    if is_scalar:
        return [mu_result.item(), dmu_result.item()]
    elif len(shape_B) == 1:
        return [mu_result.ravel(), dmu_result.ravel()]
    else:
        return [mu_result.reshape(shape_B), dmu_result.reshape(shape_B)]
