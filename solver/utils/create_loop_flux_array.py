from solver.models.VirtualArray import VirtualArray
import numpy as np 

def create_loop_flux_array(reluctance_network) -> VirtualArray:
    """
    Tạo mảng ảo flux vòng dựa trên size : tuple (số ô hàng, số ô cột)
    Kích thước loop_flux_array phụ thuộc vào kiểu tuần hoàn của lưới phụ thuộc vào kiểu
    Tuần hoàn theo first_dimension, second_dimension hoặc cả 2
    """

    # Trích xuất thông tin mạng từ trở
    cyclic_type = reluctance_network.cyclic_type # kiểu tuần hoàn
    number_of_row = reluctance_network.size[0]
    number_of_col  = reluctance_network.size[1]

    if cyclic_type =="no_cyclic": # Kiểu mạng không tuần hoàn theo trục nào 
        number_of_row = number_of_row -1
        number_of_col = number_of_col -1

    elif cyclic_type =="first_dimension":
        number_of_row = number_of_row -1

    elif cyclic_type =="second_dimension":
        number_of_col = number_of_col -1
    else: # tuần hoàn theo cả 2 hướng ( khép kín thành mạng hình túi)
        pass # bỏ qua

    virtual_size = (number_of_row,number_of_col)

    # Tổng số phần tử
    loop_flux_array_size = virtual_size[0] * virtual_size[1]

    # Vector cột (N, 1) toàn 0
    loop_flux_array = np.zeros((loop_flux_array_size, 1))

    return VirtualArray(loop_flux_array, virtual_size,cyclic_type)
