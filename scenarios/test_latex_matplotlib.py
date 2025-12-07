import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

# --- Cấu hình Matplotlib để dùng XeLaTeX (hỗ trợ Unicode/Tiếng Việt) ---

# 1. Chuyển backend sang "pgf" (phải làm trước khi gọi plt.figure)
mpl.use("pgf") 

plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    
    # 2. Key chính xác để chọn trình biên dịch
    "pgf.texsystem": "xelatex", 
    
    # 3. Key chính xác cho preamble (lưu ý: "pgf.preamble" thay vì "text.latex.preamble")
    "pgf.preamble": r"""
        \usepackage{fontspec}
        \setmainfont{Times New Roman} 
    """
    # Bạn có thể thay "Times New Roman" bằng phông chữ khác
    # như "Arial", "Calibri", "DejaVu Serif" miễn là nó hỗ trợ tiếng Việt
})
# -------------------------------------------------------------------

# Dữ liệu mẫu
x = np.linspace(0, 2 * np.pi, 400)
y = np.cos(x)

# Vẽ đồ thị
plt.figure(figsize=(8, 5)) 
plt.plot(x, y)

# --- Đặt tiêu đề bằng Tiếng Việt ---
plt.title(r'Đồ thị Sức phản điện động (BEMF) - Pha A')
plt.xlabel(r'Góc quay rôto ($\theta_r$)')
plt.ylabel(r'Điện áp ($V$)')

plt.grid(True)

# Khi dùng backend pgf, bạn nên lưu dưới dạng .pgf hoặc .pdf
plt.savefig("do_thi_tieng_viet.pdf") 
# plt.show() # .show() có thể không hoạt động tốt với pgf, ưu tiên .savefig()