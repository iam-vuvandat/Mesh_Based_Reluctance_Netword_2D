from motor_geometry.models.ReluctanceNetwork import ReluctanceNetwork
from solver.models.VirtualArray import VirtualArray
from solver.core.create_equation import create_equation
import numpy as np
from scipy.sparse.linalg import spsolve
import matplotlib.pyplot as plt
# Đã loại bỏ import find_adaptive_damping_factor
from solver.core.find_equation_component import find_equation_component

def newton_raphson(reluctance_network, iterations=20, max_relative_residual=0.005, detail_debug=False):
    
    R, F_source, J, G_truoc = find_equation_component( 
        reluctance_network=reluctance_network,
        find_R=True, find_F=True, find_J=False, find_G=True, P=None, F_input=None 
    )
    
    P = None
    try:
        P = spsolve(R, F_source)
    except Exception as e:
        if detail_debug:
            print(f"Loi khi giai R nhan P bang F. Su dung P hien tai cua mang luoi.")
    
    if P is None:
        P = reluctance_network.loop_flux_array.get_1D_array()

    relative_err = 10.0
    residual_history = []
    
    # Gán alpha cố định theo yêu cầu (alpha = 0.6)
    alpha = 0.6
    
    # Cập nhật P vào mạng lưới và tính G ban đầu G_truoc
    R, F_dummy, J, G_truoc = find_equation_component(
        reluctance_network=reluctance_network,
        find_R=True, find_F=False, find_J=False, find_G=True, P=P, F_input=F_source
    )
    
    for i in range(1, iterations + 1):
        
        # 1. TINH J VA G_SAU CHO NGHIEM P HIEN TAI
        R, F_dummy, J, G_sau = find_equation_component(
            reluctance_network=reluctance_network,
            find_R=True, find_F=False, find_J=True, find_G=True, P=P, F_input=F_source
        )
        
        P_k = reluctance_network.loop_flux_array 

        # 2. DANH GIA SAI SO BANG CHUAN PHAN DU SAI KHAC TUONG DOI
        
        # Chi tinh sai so tu buoc lap thu 2 tro di
        if i > 1:
            delta_G_norm = np.linalg.norm(G_sau - G_truoc)
            G_sau_norm = np.linalg.norm(G_sau)
            
            relative_err = delta_G_norm / G_sau_norm if G_sau_norm > 1e-12 else delta_G_norm
            residual_history.append(relative_err)
            
            if detail_debug:
                print(f"Lap {i:02d}: Sai so tuong doi = {relative_err:.6f}")
        
            # 3. KIEM TRA DIEU KIEN THOAT
            if relative_err <= max_relative_residual:
                break
        
        # 4. TINH BUOC NHAY (LUON TINH BUOC NHAY NEU CHUA THOAT)
        try:
            S = spsolve(J, -G_sau) 
        except Exception as e:
            if detail_debug:
                print(f"Loi giai tuyen tinh tai buoc {i}. Dung.")
            break
            
        # 5. CAP NHAT NGHIEM VA LUU G_SAU
        # Su dung damping factor co dinh alpha = 0.6
        P = P + alpha * S
        G_truoc = G_sau 

    # Xử lý kết quả in ra màn hình
    final_i = i if relative_err <= max_relative_residual else iterations
    final_err = relative_err if relative_err <= max_relative_residual else 10.0
    
    if relative_err <= max_relative_residual:
        print(f"Giai phap hoi tu sau {final_i} lan lap. Sai so cuoi: {final_err:.6f}")
    else:
        print(f"Giai phap khong hoi tu sau {iterations} lan lap. Sai so cuoi: {relative_err:.6f}")

    

    return reluctance_network
