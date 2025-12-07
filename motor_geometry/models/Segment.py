import numpy as np
from matplotlib.patches import Polygon as MplPolygon
import matplotlib.pyplot as plt

class Segment:
    def __init__(self, polygon, material="air", index=None, axial_length=1.0,
                 magnetic_source=0.0, delta_angle_magnetic_source=0.0,
                 stator_excitation_coeffs=None, delta_angle_stator_excitation=0.0):
        self.polygon = polygon
        self.material = material
        self.index = index
        self.axial_length = axial_length
        self.magnetic_source = magnetic_source
        self.delta_angle_magnetic_source = delta_angle_magnetic_source
        self.stator_excitation_coeffs = stator_excitation_coeffs if stator_excitation_coeffs is not None else []
        self.delta_angle_stator_excitation = delta_angle_stator_excitation
        self.segment_first_dimension_length = None
        self.segment_opening_angle = None
        self.segment_second_dimension_length = None

        self._patch = None
        self._label_text = None  # text hiển thị info

    def display(self, ax=None, show_label=False, linewidth=0.5, interactive=True):
        if ax is None:
            fig, ax = plt.subplots(figsize=(8,8))
        else:
            fig = ax.figure

        if self.polygon is not None:
            x, y = self.polygon.exterior.xy
            coords = np.column_stack((x, y))

            # Luôn viền đen, không tô màu
            facecolor = "none"
            edgecolor = "black"

            patch = MplPolygon(coords, closed=True, facecolor=facecolor,
                            edgecolor=edgecolor, linewidth=linewidth,
                            alpha=1.0, picker=interactive)
            ax.add_patch(patch)
            self._patch = patch
            patch._segment_ref = self

            if show_label:
                cx, cy = self.polygon.centroid.x, self.polygon.centroid.y
                label = f"{self.index}" if self.index is not None else str(self.material)
                self._label_text = ax.text(cx, cy, label, fontsize=6,
                                        ha='center', va='center', color='black')

        ax.set_aspect('equal')
        return ax
