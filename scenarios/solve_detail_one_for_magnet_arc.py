import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import matplotlib.pyplot as plt
import numpy as np
from ansys.utils.load_motor_cad import load_motor_cad
from ansys.core.magnetic_calculation import magnetic_calculation
from system.utils.find_locate import find_locate
from motor_geometry.models.SPM import SPM
from data.utils.data_helper import save, load

magnet_arc = 130
run_motor_cad = 1

if run_motor_cad:
    mcad = load_motor_cad(find_locate("data", "model", "5.mot"))
    mcad.set_variable("Magnet_Arc_[ED]", magnet_arc)
    fem_data = magnetic_calculation(mcad, show_plot=False)
    save(fem_var_mag_arc=fem_data)
    mcad.quit()
else:
    fem_data = load("fem_var_mag_arc")

run_rn = 1
if run_rn:
    spm = SPM()
    rn_data = spm.solve_open_circuit(show_plot=False, debug=False)
    save(rn_var_mag_arc=rn_data)
else:
    rn_data = load(f"rn_var_mag_arc")

fem_airgap = fem_data.airgap_flux_density
fem_flux = fem_data.flux_linkage
fem_bemf_ph = fem_data.back_emf_phase
fem_bemf_l = fem_data.back_emf_line
fem_cog = fem_data.cogging_torque

rn_airgap = rn_data.airgap_flux_density
rn_flux = rn_data.flux_linkage
rn_bemf_ph = rn_data.back_emf_phase
rn_bemf_l = rn_data.back_emf_line
rn_cog_energy = rn_data.cogging_torque
rn_cog_maxwell = rn_data.torque_maxwell_stress_tensor

style_fem = {"linestyle": "--", "linewidth": 1.5}
style_rn = {"linestyle": "-", "linewidth": 2.5}
color_ph1, color_ph2, color_ph3 = "red", "gold", "blue"
marker_ph1, marker_ph2, marker_ph3 = "o", "s", "^"

plt.figure(1, figsize=(10, 6))
plt.plot(fem_airgap[-1], fem_airgap[0], label="FEM - B_avg", color="black", **style_fem)
plt.plot(fem_airgap[-1], fem_airgap[1], label="FEM - B_radial", color="orange", **style_fem)
plt.plot(fem_airgap[-1], fem_airgap[2], label="FEM - B_tangential", color="blue", **style_fem)
plt.plot(rn_airgap[-1], rn_airgap[0], label="RN - B_avg", color="black", **style_rn)
plt.plot(rn_airgap[-1], rn_airgap[1], label="RN - B_radial", color="orange", **style_rn)
plt.plot(rn_airgap[-1], rn_airgap[2], label="RN - B_tangential", color="blue", **style_rn)
plt.title(f"Airgap Flux Density (Magnet Arc = {magnet_arc}°)")
plt.xlabel("Position (Degree)")
plt.ylabel("Flux Density (T)")
plt.legend(ncol=2)
plt.grid(True)
plt.tight_layout()

plt.figure(2, figsize=(10, 6))
plt.plot(fem_flux[-1], fem_flux[0], label="FEM - Phase 1", color=color_ph1, marker=marker_ph1, markevery=10, **style_fem)
plt.plot(fem_flux[-1], fem_flux[1], label="FEM - Phase 2", color=color_ph2, marker=marker_ph2, markevery=10, **style_fem)
plt.plot(fem_flux[-1], fem_flux[2], label="FEM - Phase 3", color=color_ph3, marker=marker_ph3, markevery=10, **style_fem)
plt.plot(rn_flux[-1], rn_flux[0], label="RN - Phase 1", color=color_ph1, marker=marker_ph1, markevery=10, **style_rn)
plt.plot(rn_flux[-1], rn_flux[1], label="RN - Phase 2", color=color_ph2, marker=marker_ph2, markevery=10, **style_rn)
plt.plot(rn_flux[-1], rn_flux[2], label="RN - Phase 3", color=color_ph3, marker=marker_ph3, markevery=10, **style_rn)
plt.title(f"Flux Linkage (Magnet Arc = {magnet_arc}°)")
plt.xlabel("Rotor position (Degree)")
plt.ylabel("Flux Linkage (Wb)")
plt.legend(ncol=2)
plt.grid(True)
plt.tight_layout()

plt.figure(3, figsize=(10, 6))
plt.plot(fem_bemf_ph[-1], fem_bemf_ph[0], label="FEM - Phase 1", color=color_ph1, marker=marker_ph1, markevery=10, **style_fem)
plt.plot(fem_bemf_ph[-1], fem_bemf_ph[1], label="FEM - Phase 2", color=color_ph2, marker=marker_ph2, markevery=10, **style_fem)
plt.plot(fem_bemf_ph[-1], fem_bemf_ph[2], label="FEM - Phase 3", color=color_ph3, marker=marker_ph3, markevery=10, **style_fem)
plt.plot(rn_bemf_ph[-1], rn_bemf_ph[0], label="RN - Phase 1", color=color_ph1, marker=marker_ph1, markevery=10, **style_rn)
plt.plot(rn_bemf_ph[-1], rn_bemf_ph[1], label="RN - Phase 2", color=color_ph2, marker=marker_ph2, markevery=10, **style_rn)
plt.plot(rn_bemf_ph[-1], rn_bemf_ph[2], label="RN - Phase 3", color=color_ph3, marker=marker_ph3, markevery=10, **style_rn)
plt.title(f"Phase Back EMF (Magnet Arc = {magnet_arc}°)")
plt.xlabel("Rotor position (Degree)")
plt.ylabel("Voltage (V)")
plt.legend(ncol=2)
plt.grid(True)
plt.tight_layout()

plt.figure(4, figsize=(10, 6))
plt.plot(fem_bemf_l[-1], fem_bemf_l[0], label="FEM - Line 1-2", color=color_ph1, marker=marker_ph1, markevery=10, **style_fem)
plt.plot(fem_bemf_l[-1], fem_bemf_l[1], label="FEM - Line 2-3", color=color_ph2, marker=marker_ph2, markevery=10, **style_fem)
plt.plot(fem_bemf_l[-1], fem_bemf_l[2], label="FEM - Line 3-1", color=color_ph3, marker=marker_ph3, markevery=10, **style_fem)
plt.plot(rn_bemf_l[-1], rn_bemf_l[0], label="RN - Line 1-2", color=color_ph1, marker=marker_ph1, markevery=10, **style_rn)
plt.plot(rn_bemf_l[-1], rn_bemf_l[1], label="RN - Line 2-3", color=color_ph2, marker=marker_ph2, markevery=10, **style_rn)
plt.plot(rn_bemf_l[-1], rn_bemf_l[2], label="RN - Line 3-1", color=color_ph3, marker=marker_ph3, markevery=10, **style_rn)
plt.title(f"Line-to-Line Back EMF (Magnet Arc = {magnet_arc}°)")
plt.xlabel("Rotor position (Degree)")
plt.ylabel("Voltage (V)")
plt.legend(ncol=2)
plt.grid(True)
plt.tight_layout()

plt.figure(5, figsize=(10, 6))
plt.plot(fem_cog[-1], fem_cog[0], label="FEM", color="gray", linestyle="--", linewidth=1.5)
plt.plot(rn_cog_energy[-1], rn_cog_energy[0], label="RN - Energy Method", color="red", linestyle="-", linewidth=2.5)
plt.plot(rn_cog_maxwell[-1], rn_cog_maxwell[0], label="RN - Maxwell Stress Tensor", color="green", linestyle=":", linewidth=2.5)
plt.title(f"Cogging Torque (Magnet Arc = {magnet_arc}°)")
plt.xlabel("Rotor position (Degree)")
plt.ylabel("Torque (Nm)")
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.show()