import matplotlib.pyplot as plt
import numpy as np

# Tạo dữ liệu mẫu
x = np.linspace(0, 10, 100)
y1_temp = 20 + 5 * np.sin(x)       # Dữ liệu 1: Nhiệt độ (ví dụ: từ 15 đến 25)
y2_rain = 100 + 80 * np.cos(x)  # Dữ liệu 2: Lượng mưa (ví dụ: từ 20 đến 180)

# === Bước 1: Tạo Figure và trục Y chính (bên trái) ===
fig, ax1 = plt.subplots()

# === Bước 2: Vẽ dữ liệu 1 lên ax1 ===
# Đặt màu cho đường và nhãn trục Y1 là màu xanh
color1 = 'tab:blue'
ax1.set_xlabel('Thời gian (ngày)')
ax1.set_ylabel('Nhiệt độ (°C)', color=color1)
ax1.plot(x, y1_temp, color=color1)
ax1.tick_params(axis='y', labelcolor=color1)

# === Bước 3: Tạo trục Y thứ cấp (bên phải) ===
# Lệnh .twinx() tạo ra ax2 chia sẻ chung trục X với ax1
ax2 = ax1.twinx()  

# === Bước 4: Vẽ dữ liệu 2 lên ax2 ===
# Đặt màu cho đường và nhãn trục Y2 là màu đỏ
color2 = 'tab:red'
ax2.set_ylabel('Lượng mưa (mm)', color=color2)  
ax2.plot(x, y2_rain, color=color2)
ax2.tick_params(axis='y', labelcolor=color2)

# Hiển thị đồ thị
plt.title('Đồ thị 2 trục tung (Nhiệt độ và Lượng mưa)')
fig.tight_layout()  # Đảm bảo các nhãn không bị đè lên nhau
plt.show()