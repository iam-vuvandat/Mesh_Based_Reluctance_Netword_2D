import numpy as np
import matplotlib.pyplot as plt
import scienceplots

# 1. Giữ 'no-latex'
plt.style.use(['science', 'no-latex'])

# --- SỬA TẠI ĐÂY ---
# Ghi đè cài đặt cỡ chữ của 'scienceplots'
# Bạn có thể thay đổi các số này
plt.rcParams.update({
    'font.size': 14,           # Cỡ chữ chung (nhiều mục kế thừa từ đây)
    'axes.titlesize': 16,      # Cỡ chữ Tiêu đề (thường lớn hơn một chút)
    'axes.labelsize': 14,      # Cỡ chữ nhãn X, Y
    'xtick.labelsize': 12,     # Cỡ chữ số trên trục X (thường nhỏ hơn)
    'ytick.labelsize': 12,     # Cỡ chữ số trên trục Y
    'legend.fontsize': 12,     # Cỡ chữ trong chú giải (legend)
})
# --------------------


# Dữ liệu mẫu
x = np.linspace(0, 10, 500)
y1 = np.sin(x)
y2 = np.cos(x)

# Tạo figure và axes
fig, ax = plt.subplots(figsize=(6, 4))

# Nhãn legend (chứa ký tự toán)
ax.plot(x, y1, label=r'$\sin(x)$', linestyle='-', linewidth=1.5)
ax.plot(x, y2, label=r'$\cos(x)$', linestyle='--', linewidth=1.5)

# 3. Đặt nhãn trục và tiêu đề
ax.set_xlabel(r'Rotor Angle ($\theta_r$)')
ax.set_ylabel(r'Voltage ($V$)')

# --- TIÊU ĐỀ PHỨC TẠP HƠN ---
# Hiển thị alpha mũ beta và các công thức khác
ax.set_title(r'Complex Title: $\alpha^{\beta}$ and $x_{i+1} = \frac{y_i}{z^2}$')

# Legend, grid (Dùng cài đặt từ script trước)
ax.legend(frameon=True, loc='best')
ax.grid(True, which='both', linestyle='--', linewidth=0.5)

# Lưu ra file
#plt.savefig('complex_math_plot_large_font.pdf')
#plt.savefig('complex_math_plot_large_font.png', dpi=300)

# Hiển thị đồ thị
plt.show()