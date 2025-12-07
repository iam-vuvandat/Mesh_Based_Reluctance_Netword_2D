import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from matplotlib.pylab import False_
import matplotlib.pyplot as plt
import numpy as np
import ansys.motorcad.core as pymotorcad
from system.utils.find_locate import find_locate
from ansys.utils.load_motor_cad import load_motor_cad
from ansys.core.magnetic_calculation import magnetic_calculation
from motor_geometry.models.SPM import SPM
from data.utils.data_helper import save, load

airgap = 1.5
run_motor_cad = 0
if run_motor_cad:
    mcad = load_motor_cad(r"C:\Users\Surface\Desktop\5.mot")
    #mcad = load_motor_cad(find_locate("data", "model", "5.mot"))
    mcad.set_variable("AirGap", airgap)
    fem_data = magnetic_calculation(mcad, show_plot=False)
    mcad.quit()
    save(fem1=fem_data)
else:
    fem_data = load("fem1")

run_rn = 1
if run_rn:
    spm = SPM(air_gap=airgap * 1e-3)
    rn_data = spm.solve_open_circuit(show_plot=False, debug=True,quality = "medium")
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
rn_cog_energy = rn_data.cogging_torque
rn_cog_maxwell = rn_data.torque_maxwell_stress_tensor


plt.rcParams.update({
    "font.size": 14,
    "font.family": "Times New Roman",
    "axes.labelsize": 14,
    "axes.titlesize": 14,
    "legend.fontsize": 9,
    "lines.linewidth": 1.5,
    "lines.markersize": 6
})

style_fem = {"linestyle": "--", "linewidth": 1.0}
style_rn = {"linestyle": "-", "linewidth": 2.0}
color_ph = ["r", "gold", "b"]
marker_ph = ["o", "s", "^"]

def plot_ieee(x, y_list, labels, title, xlabel, ylabel):
    plt.figure(figsize=(8, 5))
    for y, label, color, marker in zip(y_list, labels, color_ph, marker_ph):
        plt.plot(x, y, label=label, color=color, marker=marker, markevery=10)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)
    plt.legend(ncol=2)
    plt.tight_layout()

# Air-gap Flux Density (IEEE style, different markers)
plt.figure(figsize=(8, 5))
# FEM
plt.plot(fem_airgap[-1], fem_airgap[0], label="FEM - B", color="k", linestyle="--", marker="o", markevery=10)
plt.plot(fem_airgap[-1], fem_airgap[1], label="FEM - Br", color="orange", linestyle="--", marker="s", markevery=10)
plt.plot(fem_airgap[-1], fem_airgap[2], label="FEM - Bt", color="blue", linestyle="--", marker="^", markevery=10)
# RN
plt.plot(rn_airgap[-1], rn_airgap[0], label="RN - Flux density average", color="k", linestyle="-", marker="o", markevery=10)
plt.plot(rn_airgap[-1], rn_airgap[1], label="RN - Flux density radial", color="orange", linestyle="-", marker="s", markevery=10)
plt.plot(rn_airgap[-1], rn_airgap[2], label="RN - Flux density tangential", color="blue", linestyle="-", marker="^", markevery=10)

plt.title("Air-gap Flux Density")
plt.xlabel("Rotor position [deg]")
plt.ylabel("Flux Density [T]")
plt.grid(True, which="both", linestyle="--", linewidth=0.5)
plt.legend(ncol=2)
plt.tight_layout()


# Flux Linkage
plt.figure(figsize=(8, 5))
for i in range(3):
    plt.plot(fem_flux[-1], fem_flux[i], label=f"FEM - Phase {i+1}", color=color_ph[i], marker=marker_ph[i], markevery=10, linestyle="--")
    plt.plot(rn_flux[-1], rn_flux[i], label=f"RN - Phase {i+1}", color=color_ph[i], marker=marker_ph[i], markevery=10, linestyle="-")
plt.title("Flux Linkage")
plt.xlabel("Rotor position [deg]")
plt.ylabel("Flux Linkage [Wb-turns]")
plt.grid(True, which="both", linestyle="--", linewidth=0.5)
plt.legend(ncol=2)
plt.tight_layout()

# Phase Back EMF
plt.figure(figsize=(8, 5))
for i in range(3):
    plt.plot(fem_bemf_ph[-1], fem_bemf_ph[i], label=f"FEM - Phase {i+1}", color=color_ph[i], marker=marker_ph[i], markevery=10, linestyle="--")
    plt.plot(rn_bemf_ph[-1], rn_bemf_ph[i], label=f"RN - Phase {i+1}", color=color_ph[i], marker=marker_ph[i], markevery=10, linestyle="-")
plt.title("Phase Back EMF")
plt.xlabel("Rotor position [deg]")
plt.ylabel("Voltage [V]")
plt.grid(True, which="both", linestyle="--", linewidth=0.5)
plt.legend(ncol=2)
plt.tight_layout()

# Line-to-Line Back EMF
plt.figure(figsize=(8, 5))
for i in range(3):
    plt.plot(fem_bemf_l[-1], fem_bemf_l[i], label=f"FEM - Line {i+1}", color=color_ph[i], marker=marker_ph[i], markevery=10, linestyle="--")
    plt.plot(rn_bemf_l[-1], rn_bemf_l[i], label=f"RN - Line {i+1}", color=color_ph[i], marker=marker_ph[i], markevery=10, linestyle="-")
plt.title("Line-to-Line Back EMF")
plt.xlabel("Rotor position [deg]")
plt.ylabel("Voltage [V]")
plt.grid(True, which="both", linestyle="--", linewidth=0.5)
plt.legend(ncol=2)
plt.tight_layout()

# Cogging Torque Comparison
plt.figure(figsize=(8, 5))
plt.plot(fem_cog[-1], fem_cog[0], label="FEM", color="gray", linestyle="--")
plt.plot(rn_cog_energy[-1], rn_cog_energy[0], label="RN - Energy Method", color="red", linestyle="-")
plt.plot(rn_cog_maxwell[-1], rn_cog_maxwell[0], label="RN - Maxwell Stress Tensor", color="green", linestyle=":")
plt.title("Cogging Torque Comparison")
plt.xlabel("Rotor position [deg]")
plt.ylabel("Torque [Nm]")
plt.grid(True, which="both", linestyle="--", linewidth=0.5)
plt.legend()
plt.tight_layout()

plt.show()