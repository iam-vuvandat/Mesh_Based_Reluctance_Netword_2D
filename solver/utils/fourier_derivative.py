import numpy as np

def fourier_derivative(y, x):
    """
    Tính đạo hàm bằng phổ Fourier cho dữ liệu tuần hoàn.
    y: giá trị hàm (flux_linkage, coenergy, ...), 1D numpy array
    x: biến góc (theta, đơn vị rad hoặc độ đều nhau)
    """
    n = len(y)
    L = x[-1] - x[0]
    k = 2 * np.pi * np.fft.fftfreq(n, d=L/n)  # vector số sóng
    dy = np.fft.ifft(1j * k * np.fft.fft(y)).real
    return dy
