import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  

import matplotlib.pyplot as plt
import ansys.motorcad.core as pymotorcad
from system.utils.find_locate import find_locate
import numpy as np 
from ansys.utils.load_motor_cad import load_motor_cad
from ansys.core.magnetic_calculation import magnetic_calculation
from motor_geometry.models.SPM import SPM
from data.utils.get_waveform_nrmse import get_waveform_nrmse
from data.utils.get_amplitude_error import get_amplitude_error
from data.utils.data_helper import save, load
from tqdm import tqdm 

plt.rcParams['font.family'] = 'Times New Roman'

n_point = 20
airgap_min = 0.5 
airgap_max = 5.0 
airgap_variable = np.linspace(airgap_min, airgap_max, n_point)
run_motor_cad = True
if run_motor_cad == True: 
    fem_data = []
    mcad = load_motor_cad(r"C:\Users\Surface\Desktop\5.mot")
    for i in range(n_point):
        mcad.set_variable("AirGap", airgap_variable[i])
        fem_data.append(magnetic_calculation(mcad, show_plot=False))
    save(data0015 = fem_data)
else:
    fem_data = load("data0015")


run_rn = True
if run_rn == True:
    rn_data = []
    for i in range(n_point):
        spm = SPM(air_gap=airgap_variable[i] * 1e-3)
        rn_data.append(spm.solve_open_circuit(show_plot=False,debug = False, quality="medium"))
    save(data0025 = rn_data)
else:
    rn_data = load("data0025")

plot = True
field_name = ["Air gap flux density",
              "airgap_flux_density_radial",
              "airgap_flux_density_tangential",
              "Flux linkage",
              "Back EMF phase",
              "back_emf_line",
              "cogging_coenergy",
              "Cogging torque",
              "FEM computation time",
              "RN computation time"]
plot_data = np.zeros((11,n_point))
if plot == True:
    for i in range(n_point):
        plot_data[0,i] = get_waveform_nrmse(fem_data[i].airgap_flux_density,rn_data[i].airgap_flux_density,row_index = 0)
        plot_data[1,i] = get_waveform_nrmse(fem_data[i].airgap_flux_density,rn_data[i].airgap_flux_density,row_index = 1)
        plot_data[2,i] = get_waveform_nrmse(fem_data[i].airgap_flux_density,rn_data[i].airgap_flux_density,row_index = 2)
        plot_data[3,i] = get_waveform_nrmse(fem_data[i].flux_linkage,rn_data[i].flux_linkage)
        plot_data[4,i] = get_waveform_nrmse(fem_data[i].back_emf_phase,rn_data[i].back_emf_phase)
        plot_data[5,i] = get_waveform_nrmse(fem_data[i].back_emf_line,rn_data[i].back_emf_line)
        plot_data[6,i] = get_waveform_nrmse(fem_data[i].cogging_torque,rn_data[i].cogging_torque)
        plot_data[7,i] = get_waveform_nrmse(fem_data[i].cogging_torque,rn_data[i].torque_maxwell_stress_tensor)
        plot_data[8,i] = fem_data[i].total_time[0]
        plot_data[9,i] = rn_data[i].total_time
        plot_data[10,i] = airgap_variable[i]

save(data3925 = plot_data)
fig, ax1 = plt.subplots(figsize=(7, 4.5))

colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:gray']
line_styles = ['-', '--', '-.', ':', '-', '--', '-.']
markers = ['o', 's', '^', 'v', 'D', 'x', '+']

skip_indices = [1, 2, 5, 6]
plot_index = 0

# --- Trục trái: NRMSE (nét đậm hơn) ---
for i in range(8):
    if i in skip_indices:
        continue
    ax1.plot(
        plot_data[10, :],
        plot_data[i, :],
        linestyle=line_styles[plot_index % len(line_styles)],
        marker=markers[plot_index % len(markers)],
        markersize=6,
        linewidth=2.0,   # nét đậm cho sai số
        color=colors[plot_index % len(colors)],
        label=field_name[i]
    )
    plot_index += 1

ax1.set_xlabel("Airgap [mm]", fontsize=12)
ax1.set_ylabel("NRMSE", fontsize=12)
ax1.grid(True, linestyle=':', linewidth=0.8)

# --- Trục phải: Thời gian (nét mảnh hơn) ---
ax2 = ax1.twinx()
ax2.plot(
    plot_data[10, :],
    plot_data[8, :] * 1.2,
    color='black',
    linestyle='--',
    marker='d',
    markersize=6,
    linewidth=1.0,   # nét mảnh
    label=field_name[8]
)
ax2.plot(
    plot_data[10, :],
    plot_data[9, :] * 1.2,
    color='black',
    linestyle='-.',
    marker='^',
    markersize=6,
    linewidth=1.0,   # nét mảnh
    label=field_name[9]
)
ax2.set_ylabel("Computation Time [s]", fontsize=12)

# --- Gộp chú thích ---
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(
    lines1 + lines2,
    labels1 + labels2,
    loc='best',
    fontsize=10,
    frameon=False
)

plt.title("Comparison of FEM and RN Results vs Airgap", fontsize=13, fontweight='bold')
plt.tight_layout()
plt.show()
