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

run_reference = False
run_test_case = True

mesh_factor_analysis = 5
mesh_factor_reference = 10
mesh_unit = 155
airgap_mesh = mesh_unit * mesh_factor_analysis
airgap_mesh_reference = mesh_factor_reference *  mesh_unit

if run_reference == True or run_test_case == True:
    mcad = load_motor_cad(r"C:\Users\Surface\Desktop\5.mot")

if run_reference == True:
    mcad.set_variable("AirgapMeshPoints_layers",airgap_mesh_reference)
    mcad.set_variable("AirgapMeshPoints_mesh",airgap_mesh_reference)
    data_reference = magnetic_calculation(mcad,show_plot= False)
    save(data7006 = data_reference)
else:
    data_reference = load("data7006")

if run_test_case == True:
    mcad.set_variable("AirgapMeshPoints_layers",airgap_mesh)
    mcad.set_variable("AirgapMeshPoints_mesh",airgap_mesh)
    data = magnetic_calculation(mcad,show_plot= False)
    save(data7007=data)
else:
    data = load("data7007")

try:
    mcad.quit()
except:
    pass

print("Plotting comparison...")

fig, axs = plt.subplots(3, 2, figsize=(15, 13))
fig.suptitle(f'Result Comparison: Reference Mesh ({airgap_mesh_reference}) vs Coarse Mesh ({airgap_mesh})', fontsize=16)

ax = axs[0, 0]
ax.plot(data_reference.airgap_flux_density[3], data_reference.airgap_flux_density[1], 'b-', label=f'Ref (Mesh={airgap_mesh_reference})')
ax.plot(data.airgap_flux_density[3], data.airgap_flux_density[1], 'r--', label=f'Test (Mesh={airgap_mesh})')
ax.set_title("Airgap Flux Density (Br Component)")
ax.set_xlabel("Angle (deg)")
ax.set_ylabel("Flux Density (T)")
ax.legend()
ax.grid(True)

ax = axs[0, 1]
ax.plot(data_reference.flux_linkage[3], data_reference.flux_linkage[0], 'b-', label=f'Ref (Mesh={airgap_mesh_reference})')
ax.plot(data.flux_linkage[3], data.flux_linkage[0], 'r--', label=f'Test (Mesh={airgap_mesh})')
ax.set_title("Flux Linkage (Phase 1)")
ax.set_xlabel("Angle (deg)")
ax.set_ylabel("Flux Linkage (Wb)")
ax.legend()
ax.grid(True)

ax = axs[1, 0]
ax.plot(data_reference.back_emf_phase[3], data_reference.back_emf_phase[0], 'b-', label=f'Ref (Mesh={airgap_mesh_reference})')
ax.plot(data.back_emf_phase[3], data.back_emf_phase[0], 'r--', label=f'Test (Mesh={airgap_mesh})')
ax.set_title("Back EMF (Phase 1)")
ax.set_xlabel("Angle (deg)")
ax.set_ylabel("Voltage (V)")
ax.legend()
ax.grid(True)

ax = axs[1, 1]
ax.plot(data_reference.back_emf_line[3], data_reference.back_emf_line[0], 'b-', label=f'Ref (Mesh={airgap_mesh_reference})')
ax.plot(data.back_emf_line[3], data.back_emf_line[0], 'r--', label=f'Test (Mesh={airgap_mesh})')
ax.set_title("Back EMF (Line 1-2)")
ax.set_xlabel("Angle (deg)")
ax.set_ylabel("Voltage (V)")
ax.legend()
ax.grid(True)

ax = axs[2, 0]
ax.plot(data_reference.cogging_torque[1], data_reference.cogging_torque[0], 'b-', label=f'Ref (Mesh={airgap_mesh_reference})')
ax.plot(data.cogging_torque[1], data.cogging_torque[0], 'r--', label=f'Test (Mesh={airgap_mesh})')
ax.set_title("Cogging Torque")
ax.set_xlabel("Angle (deg)")
ax.set_ylabel("Torque (Nm)")
ax.legend()
ax.grid(True)

ax = axs[2, 1]
ax.axis('off') 
info_text = (
    f"--- Reference ---\n"
    f"Mesh Elements: {data_reference.element_number}\n"
    f"Calculation Time: {data_reference.total_time[0]:.2f} seconds\n"
    f"\n"
    f"--- Test ---\n"
    f"Mesh Elements: {data.element_number}\n"
    f"Calculation Time: {data.total_time[0]:.2f} seconds\n"
    f"\n"
    f"--- Comparison ---\n"
    f"Speedup: {data_reference.total_time[0] / data.total_time[0]:.1f} x"
)
ax.text(0.05, 0.5, info_text, fontsize=12, va='center', ha='left', 
        bbox=dict(boxstyle='round,pad=0.5', fc='aliceblue', alpha=0.7))

plt.tight_layout(rect=[0, 0.03, 1, 0.96])
plt.show()

print("\nCalculating NRMSE...")

nrmse_cogging = get_waveform_nrmse(data_reference.cogging_torque[0], data.cogging_torque[0])
print(f"Cogging Torque NRMSE (Coarse vs Ref): {nrmse_cogging:.4f}")

amp_error_bemf = get_amplitude_error(data_reference.back_emf_phase[0], data.back_emf_phase[0])
print(f"B-EMF Phase 1 Amplitude Error (Coarse vs Ref): {amp_error_bemf:.2f} %")

