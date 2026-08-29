from __future__ import annotations

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from chromaplot.core.models import Project
from chromaplot.core.plotting import vertical_marker_values

from .dialog_geometry import restore_dialog_geometry, save_dialog_geometry


class VerticalMarkerWindow(QDialog):
    """A window showing the current vertical marker position and values"""

    position_changed = pyqtSignal(float)
    close_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.project: Project | None = None
        self._updating_position = False

        self.setWindowTitle("Vertical Marker")
        self.setModal(False)

        self.position_spin = QDoubleSpinBox()
        self.position_spin.setDecimals(4)
        self.position_spin.setRange(-1e12, 1e12)
        self.position_spin.setSingleStep(0.1)
        self.position_spin.setKeyboardTracking(False)

        self.position_label = QLabel("Position")

        position_layout = QFormLayout()
        position_layout.addRow(self.position_label, self.position_spin)

        self.values_table = QTableWidget(0, 3)
        self.values_table.setHorizontalHeaderLabels(
            [
                "Dataset",
                "Curve",
                "Value",
            ]
        )

        self.values_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.values_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.values_table.setSelectionMode(QAbstractItemView.SingleSelection)

        self.values_table.verticalHeader().setVisible(False)

        header = self.values_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

        layout = QVBoxLayout(self)
        layout.addLayout(position_layout)
        layout.addWidget(self.values_table)

        self.position_spin.valueChanged.connect(self._on_position_changed)

        self.resize(420, 300)

        restore_dialog_geometry(self, "vertical_marker")

    def set_project(self, project: Project) -> None:
        self.project = project
        self.refresh()

    def set_position(self, x: float) -> None:
        """
        Update the displayed marker position without emitting position_changed back to plot
        """

        self._updating_position = True

        try:
            self.position_spin.setValue(float(x))
        finally:
            self._updating_position = False

        self.refresh_values()

    def set_position_range(
            self,
            xmin: float,
            xmax: float,
    ) -> None:
        lower, upper = sorted((float(xmin), float(xmax)))

        self.position_spin.setRange(lower, upper)

        span = upper - lower

        if span > 0:
            self.position_spin.setSingleStep(span / 500.0)

    def refresh(self) -> None:
        if self.project is None:
            self.values_table.setRowCount(0)
            return

        marker = self.project.vertical_marker()

        if marker is None:
            self.values_table.setRowCount(0)
            return

        try:
            x = float(marker.data["x"])
        except (KeyError, TypeError, ValueError):
            return

        self.set_position(x)

    def refresh_values(self) -> None:
        if self.project is None:
            self.values_table.setRowCount(0)
            return

        x = self.position_spin.value()

        values = vertical_marker_values(self.project, x)

        self.values_table.setRowCount(len(values))

        for row, (dataset, curve, value) in enumerate(values):
            dataset_item = QTableWidgetItem(dataset.name)
            curve_item = QTableWidgetItem(curve.name)

            if value is None:
                value_text = "—"
            else:
                value_text = f"{value:.6g}"

                if curve.y_unit:
                    value_text += f" {curve.y_unit}"

            value_item = QTableWidgetItem(value_text)
            value_item.setTextAlignment(
                Qt.AlignRight | Qt.AlignVCenter
            )

            self.values_table.setItem(row, 0, dataset_item)
            self.values_table.setItem(row, 1, curve_item)
            self.values_table.setItem(row, 2, value_item)

    def _on_position_changed(self, value: float) -> None:
        if self._updating_position:
            return

        self.position_changed.emit(float(value))

    def showEvent(self, event) -> None:
        super().showEvent(event)

        restore_dialog_geometry(
            self,
            "vertical_marker",
        )


    def hideEvent(self, event) -> None:
        save_dialog_geometry(
            self,
            "vertical_marker",
        )

        super().hideEvent(event)


    def closeEvent(self, event) -> None:
        save_dialog_geometry(
            self,
            "vertical_marker",
        )

        self.close_requested.emit()
        super().closeEvent(event)