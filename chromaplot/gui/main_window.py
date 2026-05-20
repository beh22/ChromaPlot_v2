from __future__ import annotations

from pathlib import Path

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    QAction,
    QDockWidget,
    QFileDialog,
    QLabel,
    QInputDialog,
    QMainWindow,
    QMessageBox,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from chromaplot import __version__

from chromaplot.core.importers import import_dataset
from chromaplot.core.models import Project
from chromaplot.core.project_io import load_project, save_project
from chromaplot.core.plotting import autoscale_visible_curves

from .dataset_tree import DatasetTreeWidget
from .plot_canvas import PlotCanvas
from .curve_settings_panel import CurveSettingsPanel
from .plot_settings_panel import PlotSettingsPanel
from .dataset_settings_panel import DatasetSettingsPanel


class MainWindow(QMainWindow):
    """Minimal ChromaPlot v2 main window using dock widgets."""

    def __init__(self, show_empty: bool = True, version: str = __version__):
        super().__init__()

        self.project = Project(name="Untitled")
        self.project_path: Path | None = None
        self.is_dirty = False

        self.version = version
        self.setWindowTitle(f"ChromaPlot {self.version}")
        self.resize(1200, 400)

        self.dataset_tree = DatasetTreeWidget()
        self.dataset_tree.setMinimumWidth(240)

        self.plot_canvas = PlotCanvas()

        self.dataset_settings_panel = DatasetSettingsPanel()
        self.curve_settings_panel = CurveSettingsPanel()
        self.plot_settings_panel = PlotSettingsPanel()

        self.settings_tabs = QTabWidget()
        self.settings_tabs.addTab(self.dataset_settings_panel, "Dataset")
        self.settings_tabs.addTab(self.curve_settings_panel, "Curve")
        self.settings_tabs.addTab(self.plot_settings_panel, "Plot")
        self.settings_tabs.setMinimumWidth(300)

        self.settings_container = QWidget()
        settings_layout = QVBoxLayout(self.settings_container)
        settings_layout.setContentsMargins(4, 12, 4, 4)
        settings_layout.addWidget(self.settings_tabs)

        self._build_layout()
        self._build_actions()
        self._build_view_menu()
        self._connect_signals()
        self._build_status_bar()

        self.refresh_ui_from_project()
        self.mark_clean()

    # ------------------------------------------------------------------
    # UI setup
    # ------------------------------------------------------------------

    def _build_layout(self) -> None:
        """Create central plot canvas plus dockable side panels."""
        self.setCentralWidget(self.plot_canvas)

        self.dataset_dock = QDockWidget("Datasets / Curves", self)
        self.dataset_dock.setObjectName("datasets_dock")
        self.dataset_dock.setWidget(self.dataset_tree)
        self.dataset_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.dataset_dock.setFeatures(
            QDockWidget.DockWidgetMovable
            | QDockWidget.DockWidgetFloatable
            | QDockWidget.DockWidgetClosable
        )
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dataset_dock)

        self.curve_settings_dock = QDockWidget("Settings", self)
        self.curve_settings_dock.setObjectName("settings_dock")
        self.curve_settings_dock.setWidget(self.settings_container)
        self.curve_settings_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.curve_settings_dock.setFeatures(
            QDockWidget.DockWidgetMovable
            | QDockWidget.DockWidgetFloatable
            | QDockWidget.DockWidgetClosable
        )
        self.addDockWidget(Qt.RightDockWidgetArea, self.curve_settings_dock)

        # Initial dock sizing. This only sets the starting point; users can
        # resize or float docks afterwards.
        self.resizeDocks(
            [self.dataset_dock, self.curve_settings_dock],
            [280, 280],
            Qt.Horizontal,
        )

    def _build_actions(self) -> None:
        file_menu = self.menuBar().addMenu("File")

        self.new_action = QAction("New Project", self)
        self.new_action.setShortcut("Ctrl+N")
        self.new_action.triggered.connect(self.new_project)
        file_menu.addAction(self.new_action)

        self.open_action = QAction("Open Project...", self)
        self.open_action.setShortcut("Ctrl+O")
        self.open_action.triggered.connect(self.open_project)
        file_menu.addAction(self.open_action)

        file_menu.addSeparator()

        self.save_action = QAction("Save Project", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.triggered.connect(self.save_project)
        file_menu.addAction(self.save_action)

        self.save_as_action = QAction("Save Project As...", self)
        self.save_as_action.setShortcut("Ctrl+Shift+S")
        self.save_as_action.triggered.connect(self.save_project_as)
        file_menu.addAction(self.save_as_action)

        file_menu.addSeparator()

        self.import_action = QAction("Import Data...", self)
        self.import_action.setShortcut("Ctrl+I")
        self.import_action.triggered.connect(self.import_data_files)
        file_menu.addAction(self.import_action)

        file_menu.addSeparator()

        self.export_figure_action = QAction("Export Figure...", self)
        self.export_figure_action.setShortcut("Ctrl+E")
        self.export_figure_action.triggered.connect(self.export_figure)
        file_menu.addAction(self.export_figure_action)

        file_menu.addSeparator()

        self.quit_action = QAction("Quit", self)
        self.quit_action.setShortcut("Ctrl+Q")
        self.quit_action.triggered.connect(self.close)
        file_menu.addAction(self.quit_action)

    def _build_view_menu(self) -> None:
        """Add menu actions for showing/hiding docks."""
        view_menu = self.menuBar().addMenu("View")
        view_menu.addAction(self.dataset_dock.toggleViewAction())
        view_menu.addAction(self.curve_settings_dock.toggleViewAction())

    def _connect_signals(self) -> None:
        self.dataset_tree.curve_visibility_changed.connect(self.set_curve_visibility)
        self.dataset_tree.curve_selected.connect(self.on_curve_selected)
        self.dataset_tree.dataset_selected.connect(self.on_dataset_selected)
        
        self.curve_settings_panel.curve_changed.connect(self.on_curve_settings_changed)

        self.plot_settings_panel.plot_settings_changed.connect(self.on_plot_settings_changed)
        self.plot_settings_panel.autoscale_requested.connect(self.autoscale_plot)

        self.plot_canvas.preview_size_changed.connect(self.plot_settings_panel.set_current_preview_size)

        self.plot_settings_panel.use_preview_size_requested.connect(self.use_current_preview_size_for_export)

        self.dataset_tree.dataset_rename_requested.connect(self.rename_dataset)
        self.dataset_tree.dataset_remove_requested.connect(self.remove_dataset)

        self.dataset_settings_panel.dataset_changed.connect(self.on_dataset_settings_changed)
        self.dataset_settings_panel.dataset_remove_requested.connect(self.remove_dataset)
        self.dataset_settings_panel.show_all_curves_requested.connect(self.show_all_dataset_curves)
        self.dataset_settings_panel.hide_all_curves_requested.connect(self.hide_all_dataset_curves)

    def _build_status_bar(self) -> None:
        self.status_label = QLabel("")
        status = QStatusBar()
        status.addWidget(self.status_label)
        self.setStatusBar(status)
        self.update_status_summary()

    # ------------------------------------------------------------------
    # Project state
    # ------------------------------------------------------------------

    def refresh_ui_from_project(self) -> None:
        self.dataset_tree.set_project(self.project)
        self.plot_settings_panel.set_plot_settings(self.project.plot_settings)

        width, height = self.plot_canvas.current_size_inches()
        self.plot_settings_panel.set_current_preview_size(width, height)

        self.plot_canvas.set_project(self.project)
        self.update_status_summary()
        self.update_window_title()

    def redraw_plot(self) -> None:
        self.plot_canvas.redraw()
        self.update_status_summary()

    def mark_dirty(self) -> None:
        self.is_dirty = True
        self.update_window_title()

    def mark_clean(self) -> None:
        self.is_dirty = False
        self.update_window_title()

    def update_window_title(self) -> None:
        dirty_marker = "*" if self.is_dirty else ""

        if self.project_path is not None:
            display_name = self.project_path
        else:
            display_name = self.project.name or "Untitled"

        self.setWindowTitle(f"{display_name}{dirty_marker} - ChromaPlot {self.version}")

    def update_status_summary(self) -> None:
        n_datasets = len(self.project.datasets)
        n_curves = sum(len(dataset.curves) for dataset in self.project.datasets)
        n_visible = sum(
            1 for dataset in self.project.datasets for curve in dataset.curves if curve.visible
        )
        self.status_label.setText(
            f"Datasets: {n_datasets} | Curves: {n_curves} | Visible: {n_visible}"
        )

    def maybe_save_changes(self) -> bool:
        """
        Ask the user what to do with unsaved changes.

        Returns True if the current action should continue, False if cancelled.
        """
        if not self.is_dirty:
            return True

        response = QMessageBox.question(
            self,
            "Unsaved changes",
            "This project has unsaved changes. Do you want to save them?",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            QMessageBox.Save,
        )

        if response == QMessageBox.Save:
            return self.save_project()
        if response == QMessageBox.Discard:
            return True
        return False

    # ------------------------------------------------------------------
    # File actions
    # ------------------------------------------------------------------

    def new_project(self) -> None:
        if not self.maybe_save_changes():
            return

        self.project = Project(name="Untitled")
        self.project_path = None
        self.refresh_ui_from_project()
        self.mark_clean()

    def open_project(self) -> None:
        if not self.maybe_save_changes():
            return

        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open ChromaPlot project",
            "",
            "ChromaPlot Projects (*.chromaplot);;All Files (*)",
        )
        if not path:
            return

        try:
            self.project = load_project(path)
            self.project_path = Path(path)
            self.project_name = self.project_path
            self.refresh_ui_from_project()
            self.mark_clean()
            self.statusBar().showMessage(f"Opened project: {path}", 5000)
        except Exception as exc:
            QMessageBox.critical(self, "Open project failed", str(exc))

    def save_project(self) -> bool:
        if self.project_path is None:
            return self.save_project_as()

        try:
            save_project(self.project, self.project_path)
            self.mark_clean()
            self.statusBar().showMessage(f"Saved project: {self.project_path}", 5000)
            return True
        except Exception as exc:
            QMessageBox.critical(self, "Save project failed", str(exc))
            return False

    def save_project_as(self) -> bool:
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save ChromaPlot project",
            str(self.project_path or Path("untitled.chromaplot")),
            "ChromaPlot Projects (*.chromaplot);;All Files (*)",
        )
        if not path:
            return False

        try:
            save_project(self.project, path)

            self.project_path = Path(path)
            if self.project_path.suffix != ".chromaplot":
                self.project_path = self.project_path.with_suffix(".chromaplot")

            self.project_name = self.project_path

            self.mark_clean()
            self.statusBar().showMessage(f"Saved project: {self.project_path}", 5000)
            return True
        except Exception as exc:
            QMessageBox.critical(self, "Save project failed", str(exc))
            return False

    def import_data_files(self) -> None:
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Import chromatography data",
            "",
            "Chromatography Files (*.txt *.csv *.tsv *.asc);;All Files (*)",
        )
        if not paths:
            return

        imported = 0
        errors: list[str] = []

        for path in paths:
            try:
                dataset = import_dataset(path)
                self.project.add_dataset(dataset)
                imported += 1
            except Exception as exc:
                errors.append(f"{path}: {exc}")

        if imported:
            if self.project.name == "Untitled" and imported == 1 and len(self.project.datasets) == 1:
                self.project.name = self.project.datasets[0].name
            self.refresh_ui_from_project()
            self.mark_dirty()
            self.statusBar().showMessage(f"Imported {imported} dataset(s)", 5000)

        if errors:
            QMessageBox.warning(
                self,
                "Some files could not be imported",
                "\n\n".join(errors),
            )

    def export_figure(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export figure",
            "chromaplot_figure.png",
            "PNG Image (*.png);;PDF File (*.pdf);;SVG File (*.svg);;All Files (*)",
        )
        if not path:
            return

        try:
            self.plot_canvas.export_figure(path)
            self.statusBar().showMessage(f"Exported figure: {path}", 5000)
        except Exception as exc:
            QMessageBox.critical(self, "Export figure failed", str(exc))

    # ------------------------------------------------------------------
    # Tree interactions
    # ------------------------------------------------------------------

    def set_curve_visibility(self, curve_id: str, visible: bool) -> None:
        curve = self.project.get_curve(curve_id)
        if curve is None:
            return

        curve.visible = visible

        current_dataset = self.dataset_settings_panel.dataset
        if current_dataset is not None:
            self.dataset_settings_panel.set_dataset(current_dataset)

        self.redraw_plot()
        self.mark_dirty()

    def on_curve_selected(self, curve_id: str) -> None:
        curve = self.project.get_curve(curve_id)
        if curve is None:
            return

        self.curve_settings_panel.set_curve(curve)
        self.settings_tabs.setCurrentWidget(self.curve_settings_panel)
        self.statusBar().showMessage(f"Selected curve: {curve.name}", 3000)

    def on_dataset_selected(self, dataset_id: str) -> None:
        dataset = self.project.get_dataset(dataset_id)
        if dataset is None:
            return

        self.curve_settings_panel.set_curve(None)
        self.dataset_settings_panel.set_dataset(dataset)
        self.settings_tabs.setCurrentWidget(self.dataset_settings_panel)
        self.statusBar().showMessage(f"Selected dataset: {dataset.name}", 3000)

    def on_curve_settings_changed(self, curve_id: str) -> None:
        self.dataset_tree.set_project(self.project)
        self.redraw_plot()
        self.mark_dirty()

    def on_plot_settings_changed(self) -> None:
        self.redraw_plot()
        self.mark_dirty()

    def autoscale_plot(self) -> None:
        limits = autoscale_visible_curves(self.project)
        if limits is None:
            return

        xlim, ylim = limits
        self.project.plot_settings.xlim = xlim
        self.project.plot_settings.ylim = ylim

        self.plot_settings_panel.set_plot_settings(self.project.plot_settings)
        self.redraw_plot()
        self.mark_dirty()

    def rename_dataset(self, dataset_id: str) -> None:
        dataset = self.project.get_dataset(dataset_id)
        if dataset is None:
            return

        new_name, accepted = QInputDialog.getText(
            self,
            "Rename Dataset",
            "New name:",
            text=dataset.name
        )
        
        if not accepted:
            return
        
        new_name = new_name.strip()
        if not new_name:
            QMessageBox.warning(self, "Invalid name", "Dataset name cannot be empty.")
            return
        
        dataset.name = new_name
        self.dataset_tree.set_project(self.project)
        self.mark_dirty()

    def remove_dataset(self, dataset_id: str) -> None:
        dataset = self.project.get_dataset(dataset_id)
        if dataset is None:
            return

        response = QMessageBox.question(
            self,
            "Remove Dataset",
            f"Remove dataset '{dataset.name}' from the project?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if response != QMessageBox.Yes:
            return

        self.project.remove_dataset(dataset_id)
        if not self.project.datasets:
            self.project.name = "Untitled"
            self.project_path = None

        self.curve_settings_panel.set_curve(None)
        self.dataset_settings_panel.set_dataset(None)
        self.dataset_tree.set_project(self.project)
        self.redraw_plot()
        self.mark_dirty()

    # ------------------------------------------------------------------
    # Dataset settings panel interactions
    # ------------------------------------------------------------------

    def on_dataset_settings_changed(self, dataset_id: str) -> None:
        self.dataset_tree.set_project(self.project)
        self.redraw_plot()
        self.mark_dirty()

    def show_all_dataset_curves(self, dataset_id: str) -> None:
        dataset = self.project.get_dataset(dataset_id)
        if dataset is None:
            return

        for curve in dataset.curves:
            curve.visible = True
        
        self.dataset_settings_panel.set_dataset(dataset)
        self.dataset_tree.set_project(self.project)
        self.redraw_plot()
        self.mark_dirty()

    def hide_all_dataset_curves(self, dataset_id: str) -> None:
        dataset = self.project.get_dataset(dataset_id)
        if dataset is None:
            return

        for curve in dataset.curves:
            curve.visible = False
        
        self.dataset_settings_panel.set_dataset(dataset)
        self.dataset_tree.set_project(self.project)
        self.redraw_plot()
        self.mark_dirty()


    # ------------------------------------------------------------------
    # Close handling
    # ------------------------------------------------------------------

    def closeEvent(self, event) -> None:
        if self.maybe_save_changes():
            event.accept()
        else:
            event.ignore()

    def use_current_preview_size_for_export(self) -> None:
        width, height = self.plot_canvas.current_size_inches()

        self.project.plot_settings.figure_width = width
        self.project.plot_settings.figure_height = height

        self.plot_settings_panel.set_plot_settings(self.project.plot_settings)

        self.redraw_plot()
        self.mark_dirty()

