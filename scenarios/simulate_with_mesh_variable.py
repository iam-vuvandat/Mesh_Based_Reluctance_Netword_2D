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

solve_motor_cad = False
npoint = 10
mesh_unit = 155

if solve_motor_cad:
    airgap_mesh_variable = np.arange(1, npoint + 1) * mesh_unit
    airgap_mesh_variable = [int(x) for x in airgap_mesh_variable]

    mcad = load_motor_cad(r"C:\Users\Surface\Desktop\5.mot")
    data_solved = []

    for val in airgap_mesh_variable:
       
        mcad.set_variable("AirgapMeshPoints_layers", val)
        mcad.set_variable("AirgapMeshPoints_mesh", val)

        data = magnetic_calculation(mcad, show_plot=False)
        data_solved.append(data)

    save(data001=data_solved)
else:
    data_solved = load("data001")

NRMSE_error = np.zeros((9,npoint))
for i in range(npoint):
    NRMSE_error[-1,i] = data_solved[i].element_number
    NRMSE_error[0,i] = get_waveform_nrmse(data_solved[-1].airgap_flux_density, data_solved[i].airgap_flux_density,row_index=0)
    NRMSE_error[1,i] = get_waveform_nrmse(data_solved[-1].airgap_flux_density, data_solved[i].airgap_flux_density,row_index=1)
    NRMSE_error[2,i] = get_waveform_nrmse(data_solved[-1].airgap_flux_density, data_solved[i].airgap_flux_density,row_index=2)
    NRMSE_error[3,i] = get_waveform_nrmse(data_solved[-1].flux_linkage, data_solved[i].flux_linkage,row_index=0)
    NRMSE_error[4,i] = get_waveform_nrmse(data_solved[-1].back_emf_phase, data_solved[i].back_emf_phase,row_index=0)
    NRMSE_error[5,i] = get_waveform_nrmse(data_solved[-1].back_emf_line, data_solved[i].back_emf_line,row_index=0)
    NRMSE_error[6,i] = get_waveform_nrmse(data_solved[-1].cogging_torque, data_solved[i].cogging_torque,row_index=0)

for i in range(len(data_solved)):
    NRMSE_error[7,i] = float(data_solved[i].total_time[0])

save(data0056 = NRMSE_error)        
plt.rcParams['text.color'] = 'black'
plt.rcParams['axes.labelcolor'] = 'black'
plt.rcParams['axes.edgecolor'] = 'black'
plt.rcParams['xtick.color'] = 'black'
plt.rcParams['ytick.color'] = 'black'
plt.rcParams['legend.edgecolor'] = 'black'

fig, ax1 = plt.subplots(figsize=(10, 6))

signals_to_plot = [0, 3, 6]
labels = {0: "Airgap flux density", 3: "Flux linkage", 6: "Cogging torque"}
marker_styles = {0: ('o', '-'), 3: ('^', '-'), 6: ('s', '-')}
signal_colors = {0: 'red', 3: 'blue', 6: 'gold'}

for i in signals_to_plot:
    marker, linestyle = marker_styles[i]
    color = signal_colors[i]
    ax1.plot(
        NRMSE_error[-1],
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
total_time = NRMSE_error[7,:]
ax2.plot(
    NRMSE_error[-1],
    total_time,
    marker='d',
    linestyle=':',
    linewidth=1,
    markersize=6,
    color='black',
    label="Total time"
)

left_ymin, left_ymax = ax1.get_ylim()
ax1.set_ylim(0, left_ymax)
ax2.set_ylim(0, None)
right_ymin, right_ymax = ax2.get_ylim()
ax2.set_ylim(left_ymin, right_ymax * 15)

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
