import numpy as np

def matrix_product(A, B):
    """
    Nhân hai ma trận (numpy array) với nhau.
    Nếu kết quả là mảng 1x1 thì trả về số thực.
    """
    result = np.matmul(A, B)

    # Nếu kết quả là mảng 1x1 → chuyển thành float
    if isinstance(result, np.ndarray) and result.shape == (1, 1):
        return result.item()
    return result
