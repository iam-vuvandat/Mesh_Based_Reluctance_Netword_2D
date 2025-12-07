import math
pi = math.pi 

def find_solver_parameter(motor, theta_resolution_maximum=pi/200, n_point_plot=17):
    """
    Tính toán các tham số cho bộ giải motor 
    (Tương thích với các động cơ đã dùng hệ số rút gọn)

    Parameter
    motor: đối tượng động cơ cần giải
    theta_resolution_maximum: độ phân giải góc theta cho phép (rad)
    n_point_plot: Số điểm cần vẽ đồ thị (cogging, flux_linkage,...)
    
    Return:
    total_col: số cột trong mạng từ trở
    theta_resolution: độ phân giải góc 
    step_cogging: số bước nhảy khi giải cogging
    step_standard: số bước nhảy khi giải thông thường 
    n_point_cogging: số bước giải cogging 
    n_point_standard: số bước giải thường
    n_point_check : số điểm cần quét qua, có thể có điểm không giải
    """

    cogging_period = motor.cogging_period_angle         # Một chu kì tuần hoàn cogging
    total_theta = 2 * math.pi / motor.reduce_factor     # Full góc cần giải 
    n_col_cogging_min = n_point_plot                # Số cột tối thiểu trong 1 chu kì cogging

    # Số cột trong 1 chu kì cogging: làm tròn lên phép chia của chu kì và độ phân giải, nếu không đủ số lượng thì lấy n_col_cogging_min
    n_col_cogging = max((math.ceil(cogging_period / theta_resolution_maximum)),n_col_cogging_min)
    total_col = n_col_cogging * (total_theta // cogging_period) # luôn là số nguyên
    # Chuẩn hóa độ phân giải 
    theta_resolution = cogging_period / n_col_cogging
    
    step_cogging = n_col_cogging // n_col_cogging_min
    resolution_step_cogging = theta_resolution * step_cogging
    step_standard = step_cogging * (total_theta // cogging_period)
    resolution_step_standard = theta_resolution * step_standard
    # Số bước giải 
    n_point_cogging = math.ceil(cogging_period/(resolution_step_cogging))
    n_point_standard = n_point_cogging 
    n_point_check = n_col_cogging * (total_theta // cogging_period)

    # Hiệu chỉnh: tăng số điểm giải thêm 1 cho đủ dữ liệu: 
    n_point_cogging = n_point_cogging  + 1 
    n_point_standard += 1 
    n_point_check += 1
    
    return int(total_col), theta_resolution, int(step_cogging), int(step_standard), int(n_point_cogging), int(n_point_standard), int(n_point_check)