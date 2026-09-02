from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backend_bases import MouseButton
from matplotlib.figure import Figure

from chromaplot.core.models import Project
from chromaplot.core.plotting import plot_project

from PyQt5.QtCore import Qt, pyqtSignal

class PlotCanvas(FigureCanvas):
    """Matplotlib canvas for displaying a ChromaPlot Project."""

    preview_size_changed = pyqtSignal(float, float)
    vertical_marker_moved = pyqtSignal(float)

    def __init__(self, parent=None):
        self.figure = Figure(figsize=(8, 5))
        self.ax = self.figure.add_subplot(111)
        super().__init__(self.figure)

        self._region_selection_callback = None
        self._region_selection_start_x = None
        self._region_selection_patch = None

        self._dragging_vertical_marker = False
        self._vertical_marker_pick_tolerance = 8

        self.mpl_connect("button_press_event", self._on_mouse_press)
        self.mpl_connect("motion_notify_event", self._on_mouse_move)
        self.mpl_connect("button_release_event", self._on_mouse_release)

        self.setFocusPolicy(Qt.StrongFocus)

        self.setParent(parent)
        self.project: Project | None = None

    def set_project(self, project: Project) -> None:
        self.project = project
        self.redraw()

    def redraw(self) -> None:
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)

        if self.project is not None:
            plot_project(self.project, ax=self.ax)
        else:
            self.ax.set_xlabel("Volume (mL)")
            self.ax.set_ylabel("Signal")

        self.apply_layout()
        self.draw_idle()

    def apply_layout(self) -> None:
        """Recalculate the matplotlib layout for the current canvas size."""
        try:
            self.figure.tight_layout()
        except Exception:
            pass

    def resizeEvent(self, event) -> None:
        """Re-apply layout when the Qt widget is resized."""
        super().resizeEvent(event)
        self.apply_layout()
        self.draw_idle()

        width, height = self.current_size_inches()
        self.preview_size_changed.emit(width, height)
    
    def current_size_inches(self) -> tuple[float, float]:
        """Return the current matplotlib preview figure size in inches."""
        width, height = self.figure.get_size_inches()
        return float(width), float(height)

    def export_figure(self, path: str, dpi: int = 300) -> None:
        """
        Export using the fixed project figure size, not the current GUI size.
        """

        import matplotlib as mpl

        mpl.rcParams["pdf.fonttype"] = 42
        mpl.rcParams["ps.fonttype"] = 42

        if self.project is None:
            return

        fig, ax = plt.subplots(
            figsize=(
                self.project.plot_settings.figure_width,
                self.project.plot_settings.figure_height,
            )
        )

        plot_project(self.project, ax=ax, for_export=True)
        fig.tight_layout()
        fig.savefig(path, dpi=dpi)
        plt.close(fig)

    def start_region_selection(self, callback) -> None:
        self._region_selection_callback = callback
        self._region_selection_start_x = None
        self.setCursor(Qt.CrossCursor)

    def _on_mouse_press(self, event) -> None:
        # Region selection takes priority over marker interaction.
        if self._region_selection_callback is not None:
            if event.inaxes != self.ax or event.xdata is None:
                return

            self._region_selection_start_x = event.xdata
            return

        if event.button != MouseButton.LEFT:
            return

        if event.inaxes != self.ax or event.xdata is None:
            return

        if self._vertical_marker_is_near_event(event):
            self._dragging_vertical_marker = True
            self.setCursor(Qt.SizeHorCursor)
            self.setFocus()

            self.move_vertical_marker(event.xdata)

    def _on_mouse_move(self, event) -> None:
        # Shaded-region selection.
        if self._region_selection_callback is not None:
            if self._region_selection_start_x is None:
                return
            if event.inaxes != self.ax or event.xdata is None:
                return

            x0 = self._region_selection_start_x
            x1 = event.xdata
            xmin, xmax = sorted((x0, x1))

            if self._region_selection_patch is not None:
                self._region_selection_patch.remove()

            self._region_selection_patch = self.ax.axvspan(
                xmin,
                xmax,
                color="#999999",
                alpha=0.25,
                zorder=10,
            )

            self.draw_idle()
            return

        # Vertical-marker dragging.
        if self._dragging_vertical_marker:
            if event.inaxes != self.ax or event.xdata is None:
                return

            self.move_vertical_marker(event.xdata)
            return

        # Change cursor when hovering near the marker.
        if self._vertical_marker_is_near_event(event):
            self.setCursor(Qt.SizeHorCursor)
        else:
            self.unsetCursor()

    def _on_mouse_release(self, event) -> None:
        # Finish shaded-region selection.
        if self._region_selection_callback is not None:
            if self._region_selection_start_x is None:
                return
            if event.inaxes != self.ax or event.xdata is None:
                return

            x0 = self._region_selection_start_x
            x1 = event.xdata
            xmin, xmax = sorted((x0, x1))

            if self._region_selection_patch is not None:
                self._region_selection_patch.remove()
                self._region_selection_patch = None

            callback = self._region_selection_callback
            self._region_selection_callback = None
            self._region_selection_start_x = None
            self.unsetCursor()

            self.draw_idle()

            callback(xmin, xmax)
            return

        # Finish vertical-marker dragging.
        if self._dragging_vertical_marker:
            if event.inaxes == self.ax and event.xdata is not None:
                self.move_vertical_marker(event.xdata)

            self._dragging_vertical_marker = False
            self.unsetCursor()

    def _vertical_marker(self):
        if self.project is None:
            return None

        marker = self.project.vertical_marker()

        if marker is None or not marker.visible:
            return None

        return marker

    def _vertical_marker_artist(self):
        marker = self._vertical_marker()

        if marker is None:
            return None

        gid = f"vertical_marker:{marker.id}"

        for line in self.ax.lines:
            if line.get_gid() == gid:
                return line

        return None

    def _vertical_marker_is_near_event(self, event) -> bool:
        marker = self._vertical_marker()

        if marker is None:
            return False

        if event.inaxes != self.ax:
            return False

        try:
            marker_x = float(marker.data["x"])
        except (KeyError, TypeError, ValueError):
            return False

        marker_pixel_x = self.ax.transData.transform(
            (marker_x, 0)
        )[0]

        return abs(event.x - marker_pixel_x) <= self._vertical_marker_pick_tolerance

    def _clamp_x_to_visible_range(self, x: float) -> float:
        xmin, xmax = self.ax.get_xlim()
        lower, upper = sorted((xmin, xmax))
        return max(lower, min(upper, float(x)))

    def move_vertical_marker(self, x: float) -> None:
        marker = self._vertical_marker()

        if marker is None:
            return

        x = self._clamp_x_to_visible_range(x)

        marker.data["x"] = x

        artist = self._vertical_marker_artist()

        if artist is not None:
            artist.set_xdata([x, x])

        self.draw_idle()
        self.vertical_marker_moved.emit(x)

    def keyPressEvent(self, event) -> None:
        marker = self._vertical_marker()

        if marker is None:
            super().keyPressEvent(event)
            return

        if event.key() not in (Qt.Key_Left, Qt.Key_Right):
            super().keyPressEvent(event)
            return

        try:
            current_x = float(marker.data["x"])
        except (KeyError, TypeError, ValueError):
            return

        xmin, xmax = self.ax.get_xlim()
        span = abs(xmax - xmin)

        if span <= 0:
            return

        if event.modifiers() & Qt.ShiftModifier:
            step = span / 50.0
        else:
            step = span / 500.0

        if event.key() == Qt.Key_Left:
            new_x = current_x - step
        else:
            new_x = current_x + step

        self.move_vertical_marker(new_x)

        event.accept()