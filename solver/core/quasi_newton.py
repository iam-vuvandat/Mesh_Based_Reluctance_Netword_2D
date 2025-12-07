from motor_geometry.models.ReluctanceNetwork import ReluctanceNetwork
from solver.models.VirtualArray import VirtualArray
from solver.core.create_equation import create_equation
# Bỏ import find_adaptive_damping_factor
import numpy as np
from scipy.sparse.linalg import spsolve
# SỬA LỖI IMPORT Ở ĐÂY:
from scipy.sparse import csc_matrix, identity 
import time


def quasi_newton(reluctance_network: ReluctanceNetwork, 
                 iterations: int = 40, 
                 max_relative_residual: float = 0.01, 
                 detail_debug: bool = False,
                 damping_factor: float = 0.05): # Sử dụng damping factor cố định
    """
    Giải hệ phi tuyến R(Phi) * Phi = F bằng phương pháp Quasi-Newton (Broyden H-Update).
    *** SỬ DỤNG DAMPING FACTOR CỐ ĐỊNH (Rất dễ phân kỳ) ***
    """
    
    print("--- Bắt đầu giải Quasi-Newton (Broyden H-Update) ---")
    start_time = time.time()

    # 1. KHỞI TẠO (Tính H0 và Phi0)
    reluctance_network.set_iron_reluctance_minimum()
    equation_component_linear = create_equation(reluctance_network=reluctance_network)
    J0 = equation_component_linear.R 
    F = equation_component_linear.F 

    if np.isnan(J0.data).any() or np.isinf(J0.data).any() or np.isnan(F).any() or np.isinf(F).any():
        print("[LỖI] Phát hiện NaN/Inf trong J0 hoặc F ban đầu!")
        return reluctance_network
    print("[GỠ LỖI] Dữ liệu J0 và F không chứa NaN/Inf. (Kiểm tra OK)")

    print(f"Khởi tạo ({J0.shape[0]}x{J0.shape[0]}): Tính H0 = J0^-1 (Nghịch đảo một lần)...")
    try:
        J0_csc = J0.tocsc()
        # SỬA LỖI SỬ DỤNG Ở ĐÂY:
        H_k = spsolve(J0_csc, identity(J0.shape[0], format='csc'))
    except Exception as e:
        print(f"[LỖI] spsolve thất bại khi tính nghịch đảo H0: {e}")
        return reluctance_network
        
    print(f"Tính Phi_0 = H0 * F...")
    Phi = H_k @ F 

    # Cập nhật Phi_0 vào mạng
    reluctance_network.loop_flux_array.data = Phi
    reluctance_network.loop_flux_array = reluctance_network.loop_flux_array
        
    # 3. CHUẨN BỊ VÒNG LẶP
    equation_component_nl = create_equation(reluctance_network=reluctance_network)
    R_nl = equation_component_nl.R 
    F_nl = equation_component_nl.F
    
    f_k = R_nl.dot(Phi) - F_nl 
    
    initial_residual_norm = np.linalg.norm(f_k)
    current_residual_norm = initial_residual_norm
    
    if initial_residual_norm < 1e-12: 
        print("Hệ thống đã được giải ngay sau bước tuyến tính. Kết thúc.")
        return reluctance_network
        
    print(f"Iteration 0: Khởi tạo hoàn tất. Phần dư ban đầu = {current_residual_norm:.6e}")
    
    # 4. VÒNG LẶP QUASI-NEWTON
    for k in range(iterations):
        iter_start_time = time.time()
        
        # a. Tính bước đi (O(N^2))
        delta_Phi = - (H_k @ f_k)
        
        # b. Damping factor (CỐ ĐỊNH)
        # (Bỏ qua find_adaptive_damping_factor)
        
        # c. Cập nhật Phi
        s_k = damping_factor * delta_Phi 
        Phi = Phi + s_k
        
        # d. Cập nhật f mới (tính f_{k+1})
        reluctance_network.loop_flux_array.data = Phi
        reluctance_network.loop_flux_array = reluctance_network.loop_flux_array
        
        equation_component_nl = create_equation(reluctance_network=reluctance_network)
        f_new = equation_component_nl.R.dot(Phi) - equation_component_nl.F
        
        y_k = f_new - f_k
        
        # e. Cập nhật H (Công thức Sherman-Morrison)
        try:
            Hk_y = H_k @ y_k
            s_T_Hk = s_k @ H_k 
            s_T_Hk_y = s_T_Hk @ y_k 

            if np.abs(s_T_Hk_y) < 1e-20:
                print(f"Iter {k+1}: [CẢNH BÁO] Mẫu số Broyden quá nhỏ. Bỏ qua cập nhật H.")
            else:
                numerator_vec = s_k - Hk_y
                # np.outer yêu cầu mảng 1D dày (dense)
                numerator_mat = np.outer(numerator_vec, s_T_Hk) 
                H_k = H_k + numerator_mat / s_T_Hk_y
        except Exception as e:
            print(f"Iter {k+1}: [LỖI] Cập nhật Broyden H thất bại: {e}. Dừng.")
            break
            
        # f. Cập nhật trạng thái
        f_k = f_new
        last_residual_norm = current_residual_norm
        current_residual_norm = np.linalg.norm(f_k)
        
        iter_time = time.time() - iter_start_time
        relative_residual = current_residual_norm / (initial_residual_norm + 1e-15) 
        
        print(f"Iter {k+1}: Norm={current_residual_norm:<10.4e} (Rel: {relative_residual:<8.4f}), Damp={damping_factor:<6.4f}, Time={iter_time:<5.3f}s")

        if detail_debug:
            pass
        
        if relative_residual < max_relative_residual:
            print(f"Hội tụ đạt! (Relative Residual < {max_relative_residual})")
            break
        
        if current_residual_norm > last_residual_norm and k > 3:
            print("[CẢNH BÁO] Phần dư đang tăng (Phân kỳ). Dừng lại.")
            break
            
    # 5. KẾT THÚC
    total_time = time.time() - start_time
    print(f"--- Hoàn thành Quasi-Newton (Broyden) sau {total_time:.4f} s ---")
    
    final_relative_residual = current_residual_norm / (initial_residual_norm + 1e-15)
    print(f"Phần dư cuối cùng: {current_residual_norm:.6e} (Tương đối: {final_relative_residual:.6e})")
    
    if final_relative_residual >= max_relative_residual:
        print(f"[CẢNH BÁO] Không hội tụ sau {k+1} vòng lặp. (Target: {max_relative_residual})")
        
    return reluctance_network