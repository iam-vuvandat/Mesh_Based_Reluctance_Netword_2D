import os

def get_project_root(target_file="main.py"):
    """
    Tìm thư mục cha chứa file target_file (mặc định 'main.py') từ vị trí script đang chạy.
    
    Trả về:
        str: đường dẫn thư mục cha chứa target_file
        None: nếu không tìm thấy
    """
    current_path = os.path.abspath(os.path.dirname(__file__))  # thư mục hiện tại của file này

    while True:
        # Kiểm tra xem target_file có trong thư mục này không
        if target_file in os.listdir(current_path):
            return current_path

        # Nếu đã lên tới thư mục gốc mà vẫn không tìm thấy
        parent_path = os.path.dirname(current_path)
        if parent_path == current_path:  # đã lên tới root
            return None
        
        current_path = parent_path

# Ví dụ sử dụng
if __name__ == "__main__":
    root = get_project_root()
    if root:
        print("Thư mục chứa main.py:", root)
    else:
        print("Không tìm thấy file main.py")
