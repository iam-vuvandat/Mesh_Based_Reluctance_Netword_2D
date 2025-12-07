import math 
pi = math.pi 

def vacuum_reluctance(length, section_area):
    """
    Tính từ trở chân không (vacuum reluctance).
    
    Parameters:
        length (float): chiều dài mạch từ (m)
        section_area (float): tiết diện (m^2)
    
    Returns:
        float: từ trở (A/Wb)
    """
    mu_0 = 4 * pi * 1e-7  # độ từ thẩm chân không (H/m)
    R_vacuum = length / (mu_0 * section_area)
    return R_vacuum
