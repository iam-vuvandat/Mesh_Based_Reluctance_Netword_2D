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

solve_analisys  = False

npoint = 10
quality_begin = 0
quality = []
for i in range(npoint):
    quality.append(int(i + quality_begin))

spm = SPM()
if solve_analisys == True: 
    data_solved = []
    for i in quality:
        data_solved.append(spm.solve_open_circuit(
                            solve_airgap=True,
                            solve_flux_linkage=True,
                            solve_back_emf_phase=True,
                            solve_back_emf_line=True,
                            solve_cogging_torque=True,
                            show_plot=False,
                            debug=False,
                            save_data = True,
                            quality = i,
                            angle_unit = "degree"))
        
    save(data_9827 = data_solved)
else:
    data_solved = load("data_9827")

nsolved = len(data_solved)
NRMSE_error = np.zeros((9, nsolved))

# Reference = mức quality cuối cùng
ref = data_solved[-1]

from tqdm import tqdm

for idx in tqdm(range(nsolved), desc="Đang tính NRMSE"):
    current = data_solved[idx]

    # Dòng cuối ghi số phần tử lưới
    NRMSE_error[-1, idx] = current.element_number

    # Sai số dạng sóng: airgap flux density 3 row
    NRMSE_error[0, idx] = get_waveform_nrmse(ref.airgap_flux_density,
                                             current.airgap_flux_density,
                                             row_index=0)

    NRMSE_error[1, idx] = get_waveform_nrmse(ref.airgap_flux_density,
                                             current.airgap_flux_density,
                                             row_index=1)

    NRMSE_error[2, idx] = get_waveform_nrmse(ref.airgap_flux_density,
                                             current.airgap_flux_density,
                                             row_index=2)

    # Flux linkage
    NRMSE_error[3, idx] = get_waveform_nrmse(ref.flux_linkage,
                                             current.flux_linkage,
                                             row_index=0)

    # Back-EMF phase
    NRMSE_error[4, idx] = get_waveform_nrmse(ref.back_emf_phase,
                                             current.back_emf_phase,
                                             row_index=0)

    # Back-EMF line
    NRMSE_error[5, idx] = get_waveform_nrmse(ref.back_emf_line,
                                             current.back_emf_line,
                                             row_index=0)

    # Cogging torque
    NRMSE_error[6, idx] = get_waveform_nrmse(ref.torque_maxwell_stress_tensor,
                                             current.torque_maxwell_stress_tensor,
                                             row_index=0)
    # Total time 
    NRMSE_error[7, idx] = float(current.total_time)

save(data_9973 = NRMSE_error)
element_numbers = NRMSE_error[-1]
total_time = NRMSE_error[7]

plt.rcParams['text.color'] = 'black'
plt.rcParams['axes.labelcolor'] = 'black'
plt.rcParams['axes.edgecolor'] = 'black'
plt.rcParams['xtick.color'] = 'black'
plt.rcParams['ytick.color'] = 'black'
plt.rcParams['legend.edgecolor'] = 'black'

fig, ax1 = plt.subplots(figsize=(10, 6))

signals_to_plot = [0, 3, 6]
labels = {
    0: "Airgap flux density",
    3: "Flux linkage",
    6: "Cogging torque"
}

marker_styles = {
    0: ('o', '-'),
    3: ('^', '-'),
    6: ('s', '-'),
}

signal_colors = {
    0: 'red',
    3: 'blue',
    6: 'gold'
}

for i in signals_to_plot:
    marker, linestyle = marker_styles[i]
    color = signal_colors[i]
    ax1.plot(
        element_numbers,
        NRMSE_error[i],
        marker=marker,
        linestyle=linestyle,
        color=color,
        linewidth=2,
        markersize=7,
        label=labels[i]
    )

ax1.set_xlabel("Element number")
ax1.set_ylabel("NRMSE (%)")
ax1.grid(True, linestyle='--', linewidth=0.5, alpha=0.5)

ax2 = ax1.twinx()
ax2.plot(
    element_numbers,
    total_time,
    marker='d',
    linestyle=':',
    linewidth=1,
    markersize=6,
    color='black',
    label="Total time"
)

ax2.set_ylabel("Total time (s)", color='black')
ax2.tick_params(axis='y', labelcolor='black')

lines_left, labels_left = ax1.get_legend_handles_labels()
lines_right, labels_right = ax2.get_legend_handles_labels()

ax1.legend(
    lines_left + lines_right,
    labels_left + labels_right,
    loc='upper right',
    bbox_to_anchor=(1.0, 0.4),
    fontsize=10,
    frameon=False
)

plt.title("NRMSE vs Mesh Size with Total Solve Time", color='black')
plt.tight_layout()
plt.show()