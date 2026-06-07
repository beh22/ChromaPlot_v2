from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from chromaplot.core.models import Project
from chromaplot.core.plotting import plot_project

from PyQt5.QtCore import Qt, pyqtSignal

class PlotCanvas(FigureCanvas):
    """Matplotlib canvas for displaying a ChromaPlot Project."""

    preview_size_changed = pyqtSignal(float, float)

    def __init__(self, parent=None):
        self.figure = Figure(figsize=(8, 5))
        self.ax = self.figure.add_subplot(111)
        super().__init__(self.figure)

        self._region_selection_callback = None
        self._region_selection_start_x = None
        self._region_selection_patch = None

        self.mpl_connect("button_press_event", self._on_mouse_press)
        self.mpl_connect("motion_notify_event", self._on_mouse_move)
        self.mpl_connect("button_release_event", self._on_mouse_release)

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

        plot_project(self.project, ax=ax)
        fig.tight_layout()
        fig.savefig(path, dpi=dpi)
        plt.close(fig)

    def start_region_selection(self, callback) -> None:
        self._region_selection_callback = callback
        self._region_selection_start_x = None
        self.setCursor(Qt.CrossCursor)

    def _on_mouse_press(self, event) -> None:
        if self._region_selection_callback is None:
            return
        if event.inaxes != self.ax or event.xdata is None:
            return

        self._region_selection_start_x = event.xdata

    def _on_mouse_move(self, event) -> None:
        if self._region_selection_callback is None:
            return
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

    def _on_mouse_release(self, event) -> None:
        if self._region_selection_callback is None:
            return
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