import os

def find_project_root(start_path):
    """
    Lần ngược lên trên để tìm thư mục gốc project.
    Ưu tiên: có .git, hoặc có thư mục data/motor_geometry.
    """
    path = os.path.abspath(start_path)

    while True:
        if (os.path.isdir(os.path.join(path, ".git")) or
            os.path.isdir(os.path.join(path, "data")) or
            os.path.isdir(os.path.join(path, "motor_geometry"))):
            return path

        new_path = os.path.dirname(path)
        if new_path == path:  # đã tới ổ đĩa gốc
            # Nếu không tìm thấy, trả về thư mục gốc của file bắt đầu tìm
            return os.path.abspath(start_path)
        path = new_path


def print_tree(root=None, prefix=""): # <-- THAY ĐỔI 1: Thêm root=None
    """
    In cây thư mục.
    Nếu 'root' không được cung cấp, tự động tìm thư mục gốc dự án.
    """
    
    # --- THAY ĐỔI 2: Thêm khối tự động tìm kiếm ---
    if root is None:
        # Bắt đầu tìm kiếm từ thư mục chứa file utils này
        start_search_path = os.path.dirname(os.path.abspath(__file__))
        root = find_project_root(start_search_path)
        print(f"(Tự động tìm thấy gốc dự án: {root})\n")
    # --- Hết thay đổi ---

    try:
        items = sorted(os.listdir(root))
    except FileNotFoundError:
        print(f"LỖI: Không tìm thấy thư mục '{root}'")
        return
        
    for i, item in enumerate(items):
        path = os.path.join(root, item)
        connector = "└── " if i == len(items) - 1 else "├── "
        print(prefix + connector + item)
        if os.path.isdir(path):
            new_prefix = prefix + ("    " if i == len(items) - 1 else "│   ")
            print_tree(path, new_prefix) # Gọi đệ quy


if __name__ == "__main__":
    # Khối này vẫn hoạt động như cũ khi bạn chạy file này trực tiếp
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = find_project_root(script_dir)
    print(f"Project root: {project_root}\n")
    print_tree(project_root)