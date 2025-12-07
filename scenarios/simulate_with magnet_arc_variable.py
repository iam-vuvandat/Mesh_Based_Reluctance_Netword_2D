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

FIELD_NAMES = [
    'airgap_flux_density', 
    'flux_linkage', 
    'back_emf_phase', 
    'back_emf_line', 
    'cogging_torque'
]
N_FIELDS = len(FIELD_NAMES)

plot_only = 1

n_point = 20
magnet_arc_min = 30 
magnet_arc_max = 180

magnet_arc_variable = np.linspace(magnet_arc_min, magnet_arc_max, n_point)
magnet_arc_residual = np.zeros((N_FIELDS + 1, n_point))
magnet_arc_amplitude_residual = np.zeros((N_FIELDS + 1, n_point))
Fem_data_magnet_arc = []
RN_data_magnet_arc = []

if plot_only == 0:
    mcad = load_motor_cad(find_locate("data", "model", "5.mot"))
else:
    Fem_data_magnet_arc = load("Fem_data_magnet_arc")
    RN_data_magnet_arc = load("RN_data_magnet_arc")

for i in tqdm(range(magnet_arc_variable.size), desc="Analyzing Magnet Arc", ncols=100, leave=False):
    if plot_only == 0:
        mcad.set_variable("Magnet_Arc_[ED]", magnet_arc_variable[i])
        fem_data = magnetic_calculation(mcad, show_plot=False)
        Fem_data_magnet_arc.append(fem_data)
        spm = SPM(magnet_arc=magnet_arc_variable[i])
        rn_data = spm.solve_open_circuit(show_plot=False)
        RN_data_magnet_arc.append(rn_data)
    else:
        fem_data = Fem_data_magnet_arc[i]
        rn_data = RN_data_magnet_arc[i]

    for j in range(N_FIELDS + 1):
        if j == N_FIELDS:
            magnet_arc_residual[j, i] = magnet_arc_variable[i]
            magnet_arc_amplitude_residual[j, i] = magnet_arc_variable[i]
        else:
            field_name = FIELD_NAMES[j]
            
            fem_array = getattr(fem_data, field_name)
            rn_array = getattr(rn_data, field_name)
            
            magnet_arc_residual[j, i] = get_waveform_nrmse(fem_array, rn_array)
            magnet_arc_amplitude_residual[j, i] = get_amplitude_error(fem_array, rn_array)

try:
    mcad.quit()
except:
    pass

if plot_only == 0:
    save(Fem_data_magnet_arc=Fem_data_magnet_arc)
    save(RN_data_magnet_arc=RN_data_magnet_arc)

labels = ['Air gap flux density', 'Flux linkage', 
          'Back EMF phase', 'Back EMF line', 'Cogging torque']

x_axis_nrmse = magnet_arc_residual[N_FIELDS, :] 
y_axis_nrmse = magnet_arc_residual[0:N_FIELDS, :] 

x_axis_amplitude = magnet_arc_amplitude_residual[N_FIELDS, :] 
y_axis_amplitude = magnet_arc_amplitude_residual[0:N_FIELDS, :] 

plt.figure(1, figsize=(10, 6)) 
markers_list_nrmse = ['o', 's', '^', 'x', 'D']

for i in range(y_axis_nrmse.shape[0]):
    plt.plot(x_axis_nrmse, y_axis_nrmse[i, :], 
             label=labels[i], 
             marker=markers_list_nrmse.pop(0), 
             linestyle='-') 

plt.title('NRMSE (%) between FEM and RN vs. Magnet Arc')
plt.xlabel('Magnet Arc (deg)')
plt.ylabel('NRMSE (%)')
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.figure(2, figsize=(10, 6))
markers_list_amplitude = ['o', 's', '^', 'x', 'D']

for i in range(y_axis_amplitude.shape[0]):
    plt.plot(x_axis_amplitude, y_axis_amplitude[i, :], 
             label=labels[i], 
             marker=markers_list_amplitude.pop(0), 
             linestyle='--')

plt.title('Amplitude Error (%) between FEM and RN vs. Magnet Arc')
plt.xlabel('Magnet Arc (deg)')
plt.ylabel('Amplitude Error (%)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
