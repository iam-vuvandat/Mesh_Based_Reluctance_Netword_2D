from system.core.setup import setup 
setup()
from data.utils.data_helper import load
import matplotlib.pyplot as plt
import scienceplots

plot_airgap_flux_density = True
plot_flux_linkage = True
plot_back_emf_phase = True 
plot_cogging_torque = True
plot_mesh_fem = True
plot_mesh_rn  = True
plot_var_airgap = True


plt.style.use(['science', 'no-latex'])
plt.rcParams.update({
    'font.size': 20,           # Cỡ chữ chung (nhiều mục kế thừa từ đây)
    'axes.titlesize': 30,      # Cỡ chữ Tiêu đề (thường lớn hơn một chút)
    'axes.labelsize': 25,      # Cỡ chữ nhãn X, Y
    'xtick.labelsize': 18,     # Cỡ chữ số trên trục X (thường nhỏ hơn)
    'ytick.labelsize': 18,     # Cỡ chữ số trên trục Y
    'legend.fontsize': 18,     # Cỡ chữ trong chú giải (legend)
})
colors = [
    # === Bảng màu Paul Tol (User cung cấp) ===
    # (Tốt nhất cho người mù màu, rõ ràng)
    '#4477AA',  # 0: Xanh lam (Tol)
    '#EE6677',  # 1: Đỏ (Tol)
    '#228833',  # 2: Xanh lục (Tol)
    '#CCBB44',  # 3: Vàng (Tol)
    '#66CCEE',  # 4: Xanh cyan (Tol)
    '#AA3377',  # 5: Tím (Tol)
    '#BBBBBB',  # 6: Xám (Tol)
    # === Bảng màu MATLAB (R2014b+) ===
    # (Rất hiện đại và chuyên nghiệp)
    '#0072BD',  # 7: Xanh dương (MATLAB 1)
    '#D95319',  # 8: Cam (MATLAB 2)
    '#EDB120',  # 9: Vàng (MATLAB 3)
    '#7E2F8E',  # 10: Tím (MATLAB 4)
    '#77AC30',  # 11: Xanh lục (MATLAB 5)
    '#4DBEEE',  # 12: Xanh lơ (MATLAB 6)
    '#A2142F',  # 13: Đỏ mận (MATLAB 7)
    # === Bảng màu Tableau (Mặc định Matplotlib C0-C9) ===
    # (Rất phổ biến, C0, C1, C2...)
    '#1f77b4',  # 14: Xanh lam (Tableau C0)
    '#ff7f0e',  # 15: Cam (Tableau C1)
    '#2ca02c',  # 16: Xanh lục (Tableau C2)
    '#d62728',  # 17: Đỏ (Tableau C3)
    '#9467bd',  # 18: Tím (Tableau C4)
    '#8c564b',  # 19: Nâu (Tableau C5)
    '#e377c2',  # 20: Hồng (Tableau C6)
    '#7f7f7f',  # 21: Xám (Tableau C7)
    '#bcbd22',  # 22: Vàng đất (Tableau C8)
    '#17becf',  # 23: Xanh cyan (Tableau C9)
    # === Các màu cơ bản (HTML/CSS) ===
    # (Dùng khi cần các màu chuẩn, dễ gọi tên)
    '#FF0000',  # 24: Red (Đỏ tươi)
    '#0000FF',  # 25: Blue (Xanh dương tươi)
    '#008000',  # 26: Green (Xanh lục đậm)
    '#000000',  # 27: Black (Đen)
    '#FFA500',  # 28: Orange (Cam)
    '#800080',  # 29: Purple (Tím đậm)
    '#FF00FF',  # 30: Magenta (Hồng cánh sen)
    '#808080'   # 31: Gray (Xám 50%)
]
markers = ['o', 's', '^', 'v', 'D', 'X']
linestyles = ['-', '--', ':']
if plot_airgap_flux_density == True:
    fem_data = load("fem1")
    rn_data  = load("rn1")

    # Airgap flux density
    airgap_data_fem = fem_data.airgap_flux_density
    airgap_data_rn  = rn_data.airgap_flux_density
    fig, ax = plt.subplots(figsize=(16, 10))

    ax.plot(airgap_data_fem[-1],airgap_data_fem[0], label=r'$|B|$-FEM', linestyle=linestyles[1], linewidth=1.0,marker=markers[0],markevery=20,color = colors[7])
    ax.plot(airgap_data_fem[-1],airgap_data_fem[1], label=r'$B_r$-FEM', linestyle=linestyles[1], linewidth=1.0,marker=markers[1],markevery=20,color = colors[8])
    ax.plot(airgap_data_fem[-1],airgap_data_fem[2], label=r'$B_t$-FEM', linestyle=linestyles[1], linewidth=1.0,marker=markers[2],markevery=20,color = colors[10])

    ax.plot(airgap_data_rn[-1],airgap_data_rn[0], label=r'$|B|$-MBGRN', linestyle=linestyles[0], linewidth=3.0,marker=markers[0],markevery=20,color = colors[7])
    ax.plot(airgap_data_rn[-1],airgap_data_rn[1], label=r'$B_r$-MBGRN', linestyle=linestyles[0], linewidth=3.0,marker=markers[1],markevery=20,color = colors[8])
    ax.plot(airgap_data_rn[-1],airgap_data_rn[2], label=r'$B_t$-MBGRN', linestyle=linestyles[0], linewidth=3.0,marker=markers[2],markevery=20,color = colors[10])

    ax.set_xlabel(r'Position ($Deg$)')
    ax.set_ylabel(r'Flux density ($T$)')
    ax.set_title(r'Comparison of Airgap Flux Density between FEM and MBGRN')

    ax.legend(frameon=True, loc='best',ncol=2)
    ax.grid(True, which='both', linestyle='-', linewidth=0.05)
    plt.show()

if plot_flux_linkage == True:
    # Flux linkage
    flux_linkage_fem = fem_data.flux_linkage
    flux_linkage_rn  = rn_data.flux_linkage
    fig, ax = plt.subplots(figsize=(16, 10))

    ax.plot(flux_linkage_fem[-1],flux_linkage_fem[0], label=r'Phase A-FEM', linestyle=linestyles[1], linewidth=1.0,marker=markers[0],markevery=5,color = colors[7])
    ax.plot(flux_linkage_fem[-1],flux_linkage_fem[1], label=r'Phase B-FEM', linestyle=linestyles[1], linewidth=1.0,marker=markers[1],markevery=5,color = colors[8])
    ax.plot(flux_linkage_fem[-1],flux_linkage_fem[2], label=r'Phase C-FEM', linestyle=linestyles[1], linewidth=1.0,marker=markers[2],markevery=5,color = colors[10])

    ax.plot(flux_linkage_rn[-1],flux_linkage_rn[0], label=r'Phase A-MBGRN', linestyle=linestyles[0], linewidth=3.0,marker=markers[0],markevery=5,color = colors[7])
    ax.plot(flux_linkage_rn[-1],flux_linkage_rn[1], label=r'Phase B-MBGRN', linestyle=linestyles[0], linewidth=3.0,marker=markers[1],markevery=5,color = colors[8])
    ax.plot(flux_linkage_rn[-1],flux_linkage_rn[2], label=r'Phase C-MBGRN', linestyle=linestyles[0], linewidth=3.0,marker=markers[2],markevery=5,color = colors[10])


    ax.set_xlabel(r'Rotor Position ($Deg$)')
    ax.set_ylabel(r'Flux Linkage ($Wb$)')
    ax.set_title(r'Comparison of Flux Linkage between FEM and MBGRN')

    ax.legend(frameon=True, loc='best',ncol=1)
    ax.grid(True, which='both', linestyle='-', linewidth=0.05)
    plt.show()

if plot_back_emf_phase == True:
    # Back EMF phase
    back_emf_phase_fem = fem_data.back_emf_phase
    back_emf_phase_rn  = rn_data.back_emf_phase
    fig, ax = plt.subplots(figsize=(16, 10))

    ax.plot(back_emf_phase_fem[-1],back_emf_phase_fem[0], label=r'Phase A-FEM', linestyle=linestyles[1], linewidth=1.0,marker=markers[0],markevery=5,color = colors[7])
    ax.plot(back_emf_phase_fem[-1],back_emf_phase_fem[1], label=r'Phase B-FEM', linestyle=linestyles[1], linewidth=1.0,marker=markers[1],markevery=5,color = colors[8])
    ax.plot(back_emf_phase_fem[-1],back_emf_phase_fem[2], label=r'Phase C-FEM', linestyle=linestyles[1], linewidth=1.0,marker=markers[2],markevery=5,color = colors[10])

    ax.plot(back_emf_phase_rn[-1],back_emf_phase_rn[0], label=r'Phase A-MBGRN', linestyle=linestyles[0], linewidth=3.0,marker=markers[0],markevery=5,color = colors[7])
    ax.plot(back_emf_phase_rn[-1],back_emf_phase_rn[1], label=r'Phase B-MBGRN', linestyle=linestyles[0], linewidth=3.0,marker=markers[1],markevery=5,color = colors[8])
    ax.plot(back_emf_phase_rn[-1],back_emf_phase_rn[2], label=r'Phase C-MBGRN', linestyle=linestyles[0], linewidth=3.0,marker=markers[2],markevery=5,color = colors[10])


    ax.set_xlabel(r'Rotor Position ($Deg$)')
    ax.set_ylabel(r'Back EMF ($V$)')
    ax.set_title(r'Comparison of Back EMF (Phase) between FEM and MBGRN')

    ax.legend(frameon=True, loc='lower right',ncol=1)
    ax.grid(True, which='both', linestyle='-', linewidth=0.05)
    plt.show()

if plot_cogging_torque == True:
    # Cogging torque
    cogging_fem = fem_data.cogging_torque
    cogging_rn  = rn_data.torque_maxwell_stress_tensor
    fig, ax = plt.subplots(figsize=(16, 10))

    ax.plot(cogging_fem[-1],cogging_fem[0], label=r'Cogging Torque-FEM', linestyle=linestyles[1], linewidth=1.0,color = colors[7])

    ax.plot(cogging_rn[-1],cogging_rn[0], label=r'Cogging Torque-MBGRN', linestyle=linestyles[0], linewidth=3.0,color = colors[8])

    ax.set_xlabel(r'Rotor Position ($Deg$)')
    ax.set_ylabel(r'Cogging Torque ($N/m$)')
    ax.set_title(r'Comparison of Cogging Torque between FEM and MBGRN')

    ax.legend(frameon=True, loc='lower right',ncol=1)
    ax.grid(True, which='both', linestyle='-', linewidth=0.05)
    plt.show()

if plot_mesh_fem == True:
# mesh variable fem 
    mesh_data_fem = load("data0056")
    fig, ax = plt.subplots(figsize=(16, 10))

    ax.plot(mesh_data_fem[-1], mesh_data_fem[0], label=r'Air Gap Flux Density', linestyle=linestyles[0], linewidth=3.0, color=colors[7], marker=markers[0], markevery=1)
    ax.plot(mesh_data_fem[-1], mesh_data_fem[3], label=r'Flux Linkage', linestyle=linestyles[0], linewidth=3.0, color=colors[8], marker=markers[1], markevery=1)
    ax.plot(mesh_data_fem[-1], mesh_data_fem[6], label=r'Cogging Torque', linestyle=linestyles[0], linewidth=3.0, color=colors[9], marker=markers[2], markevery=1)

    ax2 = ax.twinx()
    ax2.set_ylim(0, 4000)
    ax2.set_ylabel(r'Computation Time $(s)$')
    ax2.plot(mesh_data_fem[-1], mesh_data_fem[7], label=r'Computation Time', linestyle=linestyles[0], linewidth=1.0, color=colors[10], marker=markers[3], markevery=1)
    
    ax.set_ylim(bottom=0)
    ax2.set_ylim(bottom=0)

    ax.set_xlabel(r'Elements Number')
    ax.set_ylabel(r'NRMSE ($\%$)')
    ax.set_title(r'Dependence of Error on the Number of Mesh Elements (FEM)')

    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(handles=h1 + h2, labels=l1 + l2, frameon=True, loc='upper left', ncol=1)

    ax.grid(True, which='both', linestyle='-', linewidth=0.05)
    plt.show()

if plot_mesh_rn == True:
    mesh_data_rn = load("data_9973")
    fig, ax = plt.subplots(figsize=(16, 10))

    ax.plot(mesh_data_rn[-1], mesh_data_rn[0], label=r'Air Gap Flux Density', linestyle=linestyles[0], linewidth=3.0, color=colors[7], marker=markers[0], markevery=1)
    ax.plot(mesh_data_rn[-1], mesh_data_rn[3], label=r'Flux Linkage', linestyle=linestyles[0], linewidth=3.0, color=colors[8], marker=markers[1], markevery=1)
    ax.plot(mesh_data_rn[-1], mesh_data_rn[6], label=r'Cogging Torque', linestyle=linestyles[0], linewidth=3.0, color=colors[9], marker=markers[2], markevery=1)

    ax2 = ax.twinx()
    ax2.set_ylim(0, 30)
    ax2.set_ylabel(r'Computation Time $(s)$')
    ax2.plot(mesh_data_rn[-1], mesh_data_rn[7], label=r'Computation Time', linestyle=linestyles[0], linewidth=1.0, color=colors[10], marker=markers[3], markevery=1)
    
    ax.set_ylim(bottom=0)
    ax2.set_ylim(bottom=0)

    ax.set_xlabel(r'Elements Number')
    ax.set_ylabel(r'NRMSE ($\%$)')
    ax.set_title(r'Dependence of Error on the Number of Mesh Elements (MBGRN)')

    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(handles=h1 + h2, labels=l1 + l2, frameon=True, loc='upper left', ncol=1)

    ax.grid(True, which='both', linestyle='-', linewidth=0.05)
    plt.show()

if plot_var_airgap == True:
    data_plot = load("data3925")
    fig, ax = plt.subplots(figsize=(16, 10))
    ax.plot(data_plot[-1], mesh_data_rn[0], label=r'Air Gap Flux Density', linestyle=linestyles[0], linewidth=3.0, color=colors[7], marker=markers[0], markevery=1)

    ax2 = ax.twinx()
    ax2.plot(mesh_data_rn[-1], mesh_data_rn[8], label=r'Computation Time', linestyle=linestyles[0], linewidth=1.0, color=colors[10], marker=markers[3], markevery=1)
    ax.grid(True, which='both', linestyle='-', linewidth=0.05)
    plt.show()
