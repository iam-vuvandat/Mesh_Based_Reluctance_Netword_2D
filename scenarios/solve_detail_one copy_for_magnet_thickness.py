import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import matplotlib.pyplot as plt
import ansys.motorcad.core as pymotorcad
from system.utils.find_locate import find_locate
import numpy as np
from ansys.utils.load_motor_cad import load_motor_cad
from ansys.core.magnetic_calculation import magnetic_calculation
from motor_geometry.models.SPM import SPM
from data.utils.data_helper import save, load

magnet_thickness = 3.0

run_motor_cad = 1
if run_motor_cad == 1:
    mcad = load_motor_cad(find_locate("data","model","5.mot"))
    mcad.set_variable("Magnet_Thickness", magnet_thickness)
    fem_data = magnetic_calculation(mcad, show_plot=False)
    mcad.quit()
    save(fem1 = fem_data)
else:
    fem_data = load("fem1")

run_rn = 1
if run_rn:
    spm = SPM(
        magnet_thickness=magnet_thickness * 1e-3
    )
    rn_data = spm.solve_open_circuit(show_plot=False,debug = True)
    save(rn1=rn_data)
else:
    rn_data = load("rn1")

fem_airgap = fem_data.airgap_flux_density
fem_flux = fem_data.flux_linkage
fem_bemf_ph = fem_data.back_emf_phase
fem_bemf_l = fem_data.back_emf_line
fem_cog = fem_data.cogging_torque

rn_airgap = rn_data.airgap_flux_density
rn_flux = rn_data.flux_linkage
rn_bemf_ph = rn_data.back_emf_phase
rn_bemf_l = rn_data.back_emf_line
rn_cog = rn_data.cogging_torque

style_fem = {"linestyle": "--", "linewidth": 1.5}
style_rn = {"linestyle": "-", "linewidth": 2.5}

color_fem_1ph = "gray"
color_rn_1ph = "red"
color_ph1 = "red"
color_ph2 = "gold"
color_ph3 = "blue"

marker_ph1 = "o"
marker_ph2 = "s"
marker_ph3 = "^"

plt.figure(1, figsize=(10, 6))
plt.plot(fem_airgap[-1], fem_airgap[0], label="FEM", color=color_fem_1ph, **style_fem)
plt.plot(rn_airgap[-1], rn_airgap[0], label="RN", color=color_rn_1ph, **style_rn)
plt.title(f"Comparison: Airgap Flux Density (MagThick = {magnet_thickness}mm)")
plt.xlabel("Position (Degree)")
plt.ylabel("Flux Density (T)")
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.figure(2, figsize=(10, 6))
plt.plot(fem_flux[-1], fem_flux[0], label="FEM - Phase 1", color=color_ph1, marker=marker_ph1, markevery=10, **style_fem)
plt.plot(fem_flux[-1], fem_flux[1], label="FEM - Phase 2", color=color_ph2, marker=marker_ph2, markevery=10, **style_fem)
plt.plot(fem_flux[-1], fem_flux[2], label="FEM - Phase 3", color=color_ph3, marker=marker_ph3, markevery=10, **style_fem)
plt.plot(rn_flux[-1], rn_flux[0], label="RN - Phase 1", color=color_ph1, marker=marker_ph1, markevery=10, **style_rn)
plt.plot(rn_flux[-1], rn_flux[1], label="RN - Phase 2", color=color_ph2, marker=marker_ph2, markevery=10, **style_rn)
plt.plot(rn_flux[-1], rn_flux[2], label="RN - Phase 3", color=color_ph3, marker=marker_ph3, markevery=10, **style_rn)
plt.title(f"Comparison: Flux Linkage (MagThick = {magnet_thickness}mm)")
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
plt.title(f"Comparison: Phase Back EMF (MagThick = {magnet_thickness}mm)")
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
plt.title(f"Comparison: Line-to-Line Back EMF (MagThick = {magnet_thickness}mm)")
plt.xlabel("Rotor position (Degree)")
plt.ylabel("Voltage (V)")
plt.legend(ncol=2)
plt.grid(True)
plt.tight_layout()

plt.figure(5, figsize=(10, 6))
plt.plot(fem_cog[-1], fem_cog[0], label="FEM", color=color_fem_1ph, **style_fem)
plt.plot(rn_cog[-1], rn_cog[0], label="RN", color=color_rn_1ph, **style_rn)
plt.title(f"Comparison: Cogging Torque (MagThick = {magnet_thickness}mm)")
plt.xlabel("Rotor position (Degree)")
plt.ylabel("Torque (Nm)")
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.show()