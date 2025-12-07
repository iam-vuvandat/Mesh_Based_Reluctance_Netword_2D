import os

def find_locate(*subpaths):
    """
    Tìm đường dẫn tới file 'README.txt' từ vị trí script đang chạy,
    và cho phép truy cập các file/thư mục con từ thư mục chứa README.txt.

    Tham số:
        *subpaths: các tên file/thư mục con cần nối từ thư mục chứa README.txt

    Trả về:
        str: đường dẫn tuyệt đối tới README.txt hoặc file/thư mục con nếu truyền subpaths
        None: nếu không tìm thấy README.txt
    """
    current_path = os.path.abspath(os.path.dirname(__file__))

    while True:
        readme_file = os.path.join(current_path, "README.txt")
        if os.path.isfile(readme_file):
            # Nếu có subpaths, nối chúng vào thư mục chứa README.txt
            if subpaths:
                result = os.path.join(current_path, *subpaths)
                return os.path.abspath(result) if os.path.exists(result) else None
            return os.path.abspath(readme_file)

        parent_path = os.path.dirname(current_path)
        if parent_path == current_path:  # đã lên tới root mà không tìm thấy
            return None

        current_path = parent_path
