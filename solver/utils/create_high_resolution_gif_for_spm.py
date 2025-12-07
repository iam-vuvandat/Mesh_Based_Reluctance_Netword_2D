import sys, os, random, io, math
import matplotlib.pyplot as plt
import numpy as np
import imageio.v2 as imageio
from tqdm import tqdm 
from motor_geometry.core.extract_motor_segment import extract_motor_segment
from motor_geometry.utils.create_adaptive_trapezoid_grid_for_SPM import create_adaptive_trapezoid_grid_for_SPM
from motor_geometry.models.ReluctanceNetwork import ReluctanceNetwork
from solver.core.fixed_point_iteration import fixed_point_iteration
from solver.utils.find_solver_parameter import find_solver_parameter
from system.utils.find_locate import find_locate

pi = math.pi


def create_gif(spm, path=None, show_plot=True, debug=False):
    # 0. Tạo tên file ngẫu nhiên: SPMxxxx.gif
    rand_suffix = f"{random.randint(0, 9999):04d}"
    filename = f"SPM{rand_suffix}.gif"

    # Nếu không có path → dùng thư mục figure
    if path is None:
        folder = find_locate("figure")
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, filename)
    else:
        os.makedirs(path, exist_ok=True)
        path = os.path.join(path, filename)

    print("File GIF sẽ lưu tại: {path}")

    # 1. Extract segments
    segments = extract_motor_segment(spm, 0, 0)

    # 2. Solver parameters
    total_col, theta_resolution, step_cogging, step_standard, n_point_cogging, n_point_standard, n_point_check = find_solver_parameter(spm)
    
    # 3. Create grid
    n_rotor_yoke = 20
    n_magnet = 20
    n_airgap = 20
    n_tooth_tip = 10
    n_tooth = 20
    n_stator_yoke = 20
    n_theta = 180

    grid = create_adaptive_trapezoid_grid_for_SPM(
        spm, n_rotor_yoke, n_magnet, n_airgap, n_tooth_tip, n_tooth, n_stator_yoke, n_theta + 1
    )

    reluctance_network = ReluctanceNetwork(segments, grid, cyclic_type="first_dimension")

    number_of_rows, number_of_cols = reluctance_network.size
    ring_shift = (n_rotor_yoke + 1, n_rotor_yoke + n_magnet)
    tooth_position = int(n_rotor_yoke + n_magnet + n_airgap + n_tooth_tip + n_tooth // 2)

    frames= []

    for i in tqdm(range(180), desc="Đang tạo khung hình", unit="frame"):
    
        reluctance_network = fixed_point_iteration(reluctance_network)
        reluctance_network.shift_element(ring_shift,1)
        # Tạo frame
        fig, ax = plt.subplots(figsize=(10, 10), dpi=200)
        reluctance_network.view_flux_density(ax=ax, vmin=0.0, vmax=2.0)
        ax.set_title(f"Flux density")
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=720, bbox_inches="tight")
        buf.seek(0)
        frames.append(imageio.imread(buf))
        plt.close(fig)

    
    imageio.mimsave(path, frames, duration=0.3, loop=0)
    print(f"\n GIF đã lưu tại: {path}")

    if show_plot:
        import webbrowser
        webbrowser.open(os.path.abspath(path))
