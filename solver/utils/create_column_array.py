import numpy as np

def create_column_array(elements_list, num_elements=None):
    """
    Tạo một vector cột (mảng NumPy 2D) một cách linh hoạt.

    - **Nếu `num_elements` không được cung cấp:**
      - Hàm sẽ tạo vector cột trực tiếp từ `elements_list`.
      - Nếu `elements_list` rỗng, sẽ gây ra lỗi.
    - **Nếu `num_elements` được cung cấp:**
      - Nếu `elements_list` rỗng, hàm tạo một vector cột toàn số 0 với `num_elements` hàng.
      - Nếu `elements_list` không rỗng, hàm sẽ kiểm tra xem độ dài của list
        có khớp với `num_elements` không trước khi tạo vector.

    Args:
        elements_list (list): List chứa các phần tử của vector.
        num_elements (int, optional): Số lượng phần tử mong muốn. Mặc định là None.

    Returns:
        numpy.ndarray: Một vector cột.

    Raises:
        ValueError: Nếu có sự không hợp lệ trong các tham số đầu vào.
    """
    # Trường hợp 1: num_elements KHÔNG được cung cấp
    if num_elements is None:
        if not elements_list:
            raise ValueError("Phải cung cấp `elements_list` khi `num_elements` bị bỏ trống.")
        # Tạo vector trực tiếp từ độ dài của list
        return np.array(elements_list, dtype=float).reshape(-1, 1)

    # Trường hợp 2: num_elements ĐƯỢC cung cấp (hoạt động như phiên bản trước)
    else:
        if not elements_list:
            # Tạo vector zero nếu list rỗng
            return np.zeros((num_elements, 1), dtype=float)
        else:
            # Kiểm tra độ dài nếu list không rỗng
            if len(elements_list) != num_elements:
                raise ValueError(
                    f"Số phần tử trong list ({len(elements_list)}) không khớp với số lượng yêu cầu ({num_elements})."
                )
            # Tạo vector từ list đã được xác thực
            return np.array(elements_list, dtype=float).reshape(-1, 1)