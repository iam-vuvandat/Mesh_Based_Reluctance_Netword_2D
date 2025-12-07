import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class Grid:
    def __init__(self, grid_coordinate=None, grid_type="cartesian"):
        """
        grid_coordinate: [X_array, Y_array] numpy arrays
        grid_type: "cartesian", "trapezoid", "polar"
        """
        if not isinstance(grid_coordinate, list) or len(grid_coordinate) != 2:
            raise ValueError("grid_coordinate phải là list gồm 2 numpy arrays")

        self.grid_coordinate = grid_coordinate
        self.type = grid_type

        X_array, Y_array = self.grid_coordinate
        number_of_row = len(Y_array) - 1
        number_of_col = len(X_array) - 1

        self.size = (number_of_row, number_of_col)
        self.delta_theta = 0.0
        self.total_theta = 0.0

        if grid_type in ["trapezoid", "polar"]:
            self.delta_theta = abs(self.grid_coordinate[0][1] - self.grid_coordinate[0][0])
            self.total_theta = abs(self.delta_theta * self.size[1])

    def display(self, ax=None, linewidth=0.5, alpha=1.0, three_dimension=False, 
                z_height=0.5, show_axis=False, 
                linewidth_top=None, linewidth_vertical=None): # <--- THÊM THAM SỐ MỚI
        """
        Vẽ lưới 2D hoặc khối 3D.
        - linewidth: độ dày nét vẽ cơ bản (với 3D là mặt đáy).
        - linewidth_top: độ dày nét mặt trên (mặc định = linewidth / 7).
        - linewidth_vertical: độ dày nét cạnh đứng (mặc định = linewidth / 7).
        """
        show_plot = ax is None
        if ax is None:
            if three_dimension:
                fig = plt.figure(figsize=(8, 8))
                ax = fig.add_subplot(111, projection='3d')
                # Cố định tỉ lệ khung nhìn 3D (nếu matplotlib hỗ trợ)
                try: ax.set_box_aspect((1, 1, 1))
                except: pass
            else:
                fig, ax = plt.subplots(figsize=(8, 8))
                ax.set_aspect('equal') # <--- Cố định tỉ lệ 2D

        plot_kwargs = {'color': "#393939", 'linewidth': linewidth, 'alpha': alpha}

        X_array, Y_array = self.grid_coordinate

        # --- Xử lý độ dày nét vẽ ---
        lw_base = linewidth
        # Nếu không truyền vào thì dùng mặc định (nhạt hơn 7 lần), nếu có thì dùng giá trị truyền vào
        lw_top_val = lw_base / 7 if linewidth_top is None else linewidth_top
        lw_vert_val = lw_base / 7 if linewidth_vertical is None else linewidth_vertical

        def plot_surface_edges(X, Y):
            Z0 = np.zeros_like(X)
            Z1 = np.full_like(X, z_height)

            # --- Mặt đáy z=0: Dùng lw_base ---
            for i in range(X.shape[0]):
                ax.plot(X[i, :], Y[i, :], Z0[i, :], color='black', linewidth=lw_base, alpha=alpha)
            for j in range(X.shape[1]):
                ax.plot(X[:, j], Y[:, j], Z0[:, j], color='black', linewidth=lw_base, alpha=alpha)

            # --- Mặt trên: Dùng lw_top_val ---
            for i in range(X.shape[0]):
                ax.plot(X[i, :], Y[i, :], Z1[i, :], color='black', linewidth=lw_top_val, alpha=alpha)
            for j in range(X.shape[1]):
                ax.plot(X[:, j], Y[:, j], Z1[:, j], color='black', linewidth=lw_top_val, alpha=alpha)

            # --- Cạnh đứng: Dùng lw_vert_val ---
            for i in range(X.shape[0]):
                for j in range(X.shape[1]):
                    ax.plot([X[i,j], X[i,j]], [Y[i,j], Y[i,j]], [0, z_height], 
                            color='black', linewidth=lw_vert_val, alpha=alpha)

            # --- Căn tỉ lệ đều ---
            x_min, x_max = X.min(), X.max()
            y_min, y_max = Y.min(), Y.max()
            z_min, z_max = 0, z_height
            max_range = max(x_max-x_min, y_max-y_min, z_max-z_min)
            mid_x = (x_max+x_min)/2
            mid_y = (y_max+y_min)/2
            mid_z = (z_max+z_min)/2
            ax.set_xlim(mid_x - max_range/2, mid_x + max_range/2)
            ax.set_ylim(mid_y - max_range/2, mid_y + max_range/2)
            ax.set_zlim(mid_z - max_range/2, mid_z + max_range/2)


        # === Cartesian ===
        if self.type == "cartesian":
            XX, YY = np.meshgrid(X_array, Y_array)
            if three_dimension:
                plot_surface_edges(XX, YY)
            else:
                ax.plot(XX.T, YY.T, **plot_kwargs)
                ax.plot(XX, YY, **plot_kwargs)

        # === Trapezoid ===
        elif self.type == "trapezoid":
            Thetas, Radii = np.meshgrid(X_array, Y_array)
            X_cart = Radii * np.cos(Thetas)
            Y_cart = Radii * np.sin(Thetas)
            if three_dimension:
                plot_surface_edges(X_cart, Y_cart)
            else:
                ax.plot(X_cart.T, Y_cart.T, **plot_kwargs)
                ax.plot(X_cart, Y_cart, **plot_kwargs)

        # === Polar ===
        elif self.type == "polar":
            thetas, radii = X_array, Y_array
            if three_dimension:
                X_cart = np.array([[r * np.cos(theta) for theta in thetas] for r in radii])
                Y_cart = np.array([[r * np.sin(theta) for theta in thetas] for r in radii])
                plot_surface_edges(X_cart, Y_cart)
            else:
                import matplotlib.patches as patches
                theta_start_deg = np.rad2deg(thetas.min())
                theta_end_deg = np.rad2deg(thetas.max())
                for theta in thetas:
                    x_points = [radii.min() * np.cos(theta), radii.max() * np.cos(theta)]
                    y_points = [radii.min() * np.sin(theta), radii.max() * np.sin(theta)]
                    ax.plot(x_points, y_points, **plot_kwargs)
                for r in radii:
                    arc = patches.Arc((0,0), width=2*r, height=2*r,
                                      angle=0, theta1=theta_start_deg, theta2=theta_end_deg,
                                      **plot_kwargs)
                    ax.add_patch(arc)

        # --- Ẩn trục ---
        if three_dimension and not show_axis:
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_zticks([])
            ax.grid(False)
            ax.set_axis_off()

        if show_plot:
            plt.show()
