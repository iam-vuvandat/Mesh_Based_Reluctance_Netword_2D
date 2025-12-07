import matplotlib.pyplot as plt

def display_segments(segments, ax=None, show_label=False):
    """
    Hiển thị tất cả các segment và bật interactive.
    Khi click vào segment, nhãn thông tin xuất hiện trên figure với khung.
    Chỉ hiển thị các thuộc tính vật lý.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(12, 12))
    else:
        fig = ax.figure

    # Biến lưu text hiện tại
    current_label = {"text": None}

    def on_pick(event):
        patch = event.artist
        seg = getattr(patch, "_segment_ref", None)
        if seg is None:
            return

        # Xóa nhãn cũ nếu có
        if current_label["text"] is not None:
            current_label["text"].remove()
            current_label["text"] = None

        # Nếu click lại vào cùng segment, chỉ tắt nhãn
        if getattr(seg, "_label_text_visible", False):
            seg._label_text_visible = False
            fig.canvas.draw_idle()
            return

        # Tọa độ centroid
        cx, cy = seg.polygon.centroid.x, seg.polygon.centroid.y

        # Chỉ lấy các thuộc tính vật lý
        attrs = {
            "Material": seg.material,
            "Index": seg.index,
            "Axial length": seg.axial_length,
            "Magnetic source": seg.magnetic_source,
            "Δangle_magnetic_source": seg.delta_angle_magnetic_source,
            "Stator excitation coeffs": seg.stator_excitation_coeffs,
            "Δangle_stator_excitation": seg.delta_angle_stator_excitation,
            "First dim length": seg.segment_first_dimension_length,
            "Opening angle": seg.segment_opening_angle,
            "Second dim length": seg.segment_second_dimension_length,
        }

        # Format nội dung label
        label_lines = [f"{k}: {v}" for k, v in attrs.items()]
        label = "\n".join(label_lines)

        # Tạo nhãn mới
        text = ax.text(cx, cy, label, fontsize=7, ha='center', va='center', color='black',
                       bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'))
        current_label["text"] = text
        seg._label_text_visible = True
        fig.canvas.draw_idle()

    # Vẽ tất cả segment
    for seg in segments:
        seg.display(ax=ax, show_label=show_label, interactive=True)
        seg._label_text_visible = False

    fig.canvas.mpl_connect('pick_event', on_pick)

    # Tính bounding box
    all_bounds = [seg.polygon.bounds for seg in segments if seg.polygon is not None]
    if all_bounds:
        xmin = min(b[0] for b in all_bounds)
        ymin = min(b[1] for b in all_bounds)
        xmax = max(b[2] for b in all_bounds)
        ymax = max(b[3] for b in all_bounds)
        dx = xmax - xmin
        dy = ymax - ymin
        ax.set_xlim(xmin - 0.2*dx, xmax + 0.2*dx)
        ax.set_ylim(ymin - 0.2*dy, ymax + 0.2*dy)

    ax.set_aspect('equal', adjustable='box')
    ax.set_xlabel("X [m]")
    ax.set_ylabel("Y [m]")
    ax.set_title("Segments")

    plt.tight_layout()
    plt.show()
    return ax
