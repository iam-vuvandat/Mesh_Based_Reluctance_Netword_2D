from typing import List
import ansys.motorcad.core as pymotorcad
import numpy as np 
import matplotlib.pyplot as plt
import time 
from system.utils.print_inline import print_inline

class Output:
    def __init__(self, 
                 airgap_flux_density=None, 
                 flux_linkage=None, 
                 back_emf_phase=None, 
                 back_emf_line=None, 
                 cogging_torque=None,
                 total_time = None,
                 element_number = None):
        
        self.airgap_flux_density = airgap_flux_density
        self.flux_linkage = flux_linkage
        self.back_emf_phase = back_emf_phase
        self.back_emf_line = back_emf_line
        self.cogging_torque = cogging_torque
        self.total_time = total_time,
        self.element_number = element_number

def magnetic_calculation(mcad, show_plot=True) -> Output:
    """
    Nhận vào file cần giải, tiến hành mô phỏng bằng công cụ magnetic trong ANSYS-MOTORCAD.

    Args:
        mcad (pymotorcad.MotorCAD): Đối tượng Motor-CAD API.
        show_plot (bool): Liệu có hiển thị biểu đồ kết quả hay không.
    
    Returns:
        Output: Đối tượng dataclass chứa tất cả các kết quả tính toán dưới dạng NumPy arrays 
                và tổng thời gian tính toán.
    """
    
    time_start = time.perf_counter()
    mcad.set_variable("MessageDisplayState", 2)
    mcad.show_magnetic_context()
    mcad.do_magnetic_calculation()

    # Export data
    theta, airgap_flux_density_data = mcad.get_magnetic_graph("FluxDensityAirGap")
    _,airgap_flux_density_radial    = mcad.get_magnetic_graph("FluxDensityAirGap_Br")
    _,airgap_flux_density_tangential= mcad.get_magnetic_graph("FluxDensityAirGap_Bt")
    airgap_flux_density = np.vstack((airgap_flux_density_data,airgap_flux_density_radial,airgap_flux_density_tangential, theta))

    theta, flux_linkage1 = mcad.get_magnetic_graph("FluxLinkageOCPh1")
    _, flux_linkage2 = mcad.get_magnetic_graph("FluxLinkageOCPh2")
    _, flux_linkage3 = mcad.get_magnetic_graph("FluxLinkageOCPh3")
    flux_linkage = np.vstack((flux_linkage1, flux_linkage2, flux_linkage3, theta))

    theta, emfphase1 = mcad.get_magnetic_graph("BackEMFPh1")
    _, emfphase2 = mcad.get_magnetic_graph("BackEMFPh2")
    _, emfphase3 = mcad.get_magnetic_graph("BackEMFPh3")
    back_emf_phase = np.vstack((emfphase1, emfphase2, emfphase3, theta))

    theta, emfline1 = mcad.get_magnetic_graph("BackEMFLineToLine12")
    _, emfline2 = mcad.get_magnetic_graph("BackEMFLineToLine23")
    _, emfline3 = mcad.get_magnetic_graph("BackEMFLineToLine34")
    back_emf_line = np.vstack((emfline1, emfline2, emfline3, theta))

    theta, cogging = mcad.get_magnetic_graph("CoggingTorqueCE")
    cogging_torque = np.vstack((cogging, theta))

    element_number = mcad.get_variable("FEA_MeshElements")

    mcad.set_variable("MessageDisplayState", 0)
    if show_plot:
        print("Plotting results...")
        
        # Tạo một cửa sổ hình (figure) với 3 hàng, 2 cột
        fig, axs = plt.subplots(3, 2, figsize=(14, 12))
        fig.suptitle('Kết quả tính toán từ Motor-CAD', fontsize=16)

        # 1. Biểu đồ Mật độ từ thông khe hở (Airgap Flux Density)
        ax = axs[0, 0]
        ax.plot(airgap_flux_density[-1], airgap_flux_density[0])
        ax.plot(airgap_flux_density[-1], airgap_flux_density[1])
        ax.plot(airgap_flux_density[-1], airgap_flux_density[2])
        ax.set_title("Mật độ từ thông khe hở (Airgap Flux Density)")
        ax.set_xlabel("Góc (độ)")
        ax.set_ylabel("Flux Density (T)")
        ax.grid(True)

        # 2. Biểu đồ Liên kết từ thông (Flux Linkage)
        ax = axs[0, 1]
        ax.plot(flux_linkage[3], flux_linkage[0], label="Phase 1")
        ax.plot(flux_linkage[3], flux_linkage[1], label="Phase 2")
        ax.plot(flux_linkage[3], flux_linkage[2], label="Phase 3")
        ax.set_title("Liên kết từ thông (Flux Linkage)")
        ax.set_xlabel("Góc (độ)")
        ax.set_ylabel("Flux Linkage (Wb)")
        ax.legend()
        ax.grid(True)

        # 3. Biểu đồ Sức phản điện động (Phase Back EMF)
        ax = axs[1, 0]
        ax.plot(back_emf_phase[3], back_emf_phase[0], label="Phase 1")
        ax.plot(back_emf_phase[3], back_emf_phase[1], label="Phase 2")
        ax.plot(back_emf_phase[3], back_emf_phase[2], label="Phase 3")
        ax.set_title("Sức phản điện động (Phase Back EMF)")
        ax.set_xlabel("Góc (độ)")
        ax.set_ylabel("Voltage (V)")
        ax.legend()
        ax.grid(True)

        # 4. Biểu đồ Sức phản điện động (Line-to-Line EMF)
        ax = axs[1, 1]
        ax.plot(back_emf_line[3], back_emf_line[0], label="Line 1-2")
        ax.plot(back_emf_line[3], back_emf_line[1], label="Line 2-3")
        ax.plot(back_emf_line[3], back_emf_line[2], label="Line 3-4")
        ax.set_title("Sức phản điện động (Line-to-Line EMF)")
        ax.set_xlabel("Góc (độ)")
        ax.set_ylabel("Voltage (V)")
        ax.legend()
        ax.grid(True)

        # 5. Biểu đồ Mô-men rãnh (Cogging Torque)
        ax = axs[2, 0]
        ax.plot(cogging_torque[1], cogging_torque[0], color='r')
        ax.set_title("Mô-men rãnh (Cogging Torque)")
        ax.set_xlabel("Góc (độ)")
        ax.set_ylabel("Torque (Nm)")
        ax.grid(True)

        # Ẩn ô biểu đồ thứ 6 (vì không dùng)
        axs[2, 1].axis('off')

        # Tự động căn chỉnh bố cục và hiển thị cửa sổ
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.show()
    
    time_end = time.perf_counter()
    total_time = time_end - time_start
    print("FEM calculated: ", total_time, " second")

    # Tạo và trả về đối tượng Output với tất cả dữ liệu đã đóng gói
    return Output(
        airgap_flux_density=airgap_flux_density,
        flux_linkage=flux_linkage,
        back_emf_phase=back_emf_phase,
        back_emf_line=back_emf_line,
        cogging_torque=cogging_torque,
        total_time = total_time,
        element_number = element_number
    )
