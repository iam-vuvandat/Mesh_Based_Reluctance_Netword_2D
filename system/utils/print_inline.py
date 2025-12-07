import sys
import time

def print_inline(*args, sep=' ', line_width: int = 80):
    """
    Prints a string to the console, overwriting the current line,
    and accepting multiple arguments like the standard print() function.

    Args:
        *args: The objects to print (will be converted to strings).
        sep (str): Separator inserted between values, default is a space.
        line_width (int): The total width to clear on the line.
    """
    # 1. Chuyển đổi tất cả các đối số thành chuỗi và nối chúng bằng 'sep'
    #    (giống hệt cách hàm print() xử lý *args và sep)
    text = sep.join(map(str, args))
    
    # 2. Đệm chuỗi với dấu cách để xóa nội dung cũ
    padded_text = text.ljust(line_width)
    
    # 3. Sử dụng '\r' để di chuyển con trỏ về đầu dòng và ghi đè
    sys.stdout.write(f"\r{padded_text}")
    
    # 4. Đảm bảo văn bản được hiển thị ngay lập tức
    sys.stdout.flush()

# --- Ví dụ sử dụng (Demo) ---
if __name__ == "__main__":
    total_time = 15.678
    
    print("Starting a task...")
    
    for i in range(11):
        # Sử dụng *args, giống như hàm print()
        print_inline("Progress:", i * 10, "%", "(Running...)", sep=' -> ')
        time.sleep(0.1) 
    
    # Sử dụng như cách bạn yêu cầu
    print_inline("Time simulate:", total_time, "seconds", sep=' ', line_width=100)
    
    # In một dòng mới thông thường để kết thúc
    print() 
    print("Program finished.")