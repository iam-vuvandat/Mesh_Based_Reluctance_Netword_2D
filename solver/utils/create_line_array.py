import numpy as np

def create_line_array(elements_list=None, num_elements=None):
    """
    Tạo một vector hàng (mảng NumPy 1D) một cách linh hoạt.

    - **Trường hợp 1: Chỉ cung cấp `elements_list`**
      - Hàm sẽ tạo vector hàng trực tiếp từ `elements_list`.

    - **Trường hợp 2: Chỉ cung cấp `num_elements`**
      - Hàm sẽ tạo một vector hàng chứa toàn số 0 với độ dài `num_elements`.

    - **Trường hợp 3: Cung cấp cả hai**
      - Hàm sẽ kiểm tra xem độ dài của `elements_list` có khớp với `num_elements`
        không trước khi tạo vector.

    Args:
        elements_list (list, optional): List chứa các phần tử của vector. Mặc định là None.
        num_elements (int, optional): Số lượng phần tử mong muốn. Mặc định là None.

    Returns:
        numpy.ndarray: Một vector hàng (mảng 1D).

    Raises:
        ValueError: Nếu các tham số đầu vào không hợp lệ hoặc mâu thuẫn.
    """
    # Luồng 1: num_elements KHÔNG được cung cấp. Dựa hoàn toàn vào elements_list.
    if num_elements is None:
        if not elements_list:
            raise ValueError("Phải cung cấp `elements_list` khi `num_elements` không được chỉ định.")
        return np.array(elements_list, dtype=float)

    # Luồng 2: num_elements CÓ được cung cấp.
    else:
        # Nếu elements_list rỗng hoặc None, tạo vector zero.
        if not elements_list:
            return np.zeros(num_elements, dtype=float)
        # Nếu elements_list cũng được cung cấp, hãy xác thực nó.
        else:
            if len(elements_list) != num_elements:
                raise ValueError(
                    f"Số phần tử trong list ({len(elements_list)}) không khớp với số lượng yêu cầu ({num_elements})."
                )
            return np.array(elements_list, dtype=float)