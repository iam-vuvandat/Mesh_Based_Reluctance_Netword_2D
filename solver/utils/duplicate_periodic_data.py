import numpy as np 

def duplicate_periodic_data(data):
    y = data[:-1, :]      # các hàng dữ liệu
    x = data[-1, :]       # hàng góc rotor (theta)
    period = x[-1] - x[0] # độ dài 1 chu kỳ

    # Bỏ điểm cuối vì trùng điểm đầu
    y_main = y[:, :-1]
    x_main = x[:-1]

    # Nhân đôi
    y_dup = y_main
    x_dup = x_main + period

    # Ghép lại
    y_new = np.hstack([y_main, y_dup])
    x_new = np.hstack([x_main, x_dup])

    return np.vstack([y_new, x_new])
