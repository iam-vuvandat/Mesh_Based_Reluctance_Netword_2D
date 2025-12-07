import numpy as np
from scipy.interpolate import interp1d

MU0 = 4 * np.pi * 1e-7  # H/m

def find_maximum_permeance(material_database, n_points=5000):
    """
    Tìm độ từ thẩm tương đối cực đại (mu_r) của sắt trong material_database.
    Trả về: mu_r_max
    """
    # Lấy dữ liệu BH từ Iron
    B_TABLE = material_database.iron.B_H_curve["B_data"]
    H_TABLE = material_database.iron.B_H_curve["H_data"]

    # Nội suy H(B)
    H_interpolator = interp1d(
        B_TABLE, H_TABLE,
        kind="cubic",
        fill_value="extrapolate"
    )

    # Quét lưới B
    B_grid = np.linspace(B_TABLE[0], B_TABLE[-1], n_points)
    H_grid = H_interpolator(B_grid)

    # Tính mu_r(B) = B / (μ0 * H)
    mu_r_grid = np.divide(B_grid, MU0 * H_grid, where=H_grid != 0)

    # Lấy giá trị cực đại
    mu_r_max = np.nanmax(mu_r_grid)

    return mu_r_max
