import time
from tqdm import tqdm

# --- Cấu hình ---
TOTAL_STEPS = 50

print("Bắt đầu tác vụ...")

# SỬA LỖI:
# 1. Bọc trong khối 'with' (đã có)
# 2. Thêm leave=False một cách RÕ RÀNG để buộc tqdm xóa thanh tiến trình.
with tqdm(total=TOTAL_STEPS, 
          desc="Đang xử lý dữ liệu", 
          ncols=70, 
          colour="green",
          leave=False) as pbar: # ⬅️ THAY ĐỔI QUAN TRỌNG NHẤT
    for i in range(TOTAL_STEPS):
        # Giả lập công việc đang được thực hiện
        time.sleep(0.05)
        
        # Cập nhật tiến trình của thanh
        pbar.update(1)

# Khi khối 'with' kết thúc, thanh tiến trình được TẮT.

print("✅ Tác vụ hoàn thành. Thanh tiến trình đã tắt thành công.")
print("Dòng này được in trên một dòng sạch sẽ.")